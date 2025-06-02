import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import joblib
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import io

# --- Load Model & Artifacts ---
try:
    model = tf.keras.models.load_model('./saved-models/ls.h5')
    # Compile with run_eagerly for debugging; note: dropout is normally disabled during inference.
    model.compile(optimizer='adam', loss='mse', metrics=['mae'], run_eagerly=True)
except Exception as e:
    st.error(f"Model load error: {e}")

try:
    encoder = joblib.load('./saved-models/le.pkl')
    scaler = joblib.load('./saved-models/sc.pkl')
except Exception as e:
    st.error(f"Scaler/Encoder load error: {e}")

# --- Preprocessing Function ---
def preprocess_custom_data(new_data, seq_length=24):
    try:
        # Encode Sales_Channel using pre-fitted encoder.
        new_data['Sales_Channel'] = encoder.transform(new_data['Sales_Channel'])
        features = ['Historical_Sales', 'Customer_Trends_Score', 'Revenue', 'Sales_Channel']
        processed_data = new_data[features]
        processed_data_scaled = scaler.transform(processed_data)

        # Create sequences for LSTM input.
        x = []
        if len(processed_data_scaled) >= seq_length:
            # We generate all possible subsequences of length seq_length.
            for i in range(seq_length, len(processed_data_scaled) + 1):
                x.append(processed_data_scaled[i - seq_length:i])
        else:
            st.warning(f"⚠️ At least {seq_length} rows are needed. Only {len(processed_data_scaled)} provided.")
            return None

        x = np.array(x)
        st.write(f"Input data shape for prediction: {x.shape}")
        return x
    except Exception as e:
        st.error(f"Preprocessing error: {e}")
        return None

# --- Multi-step Forecasting Function ---
def multi_step_forecast(initial_sequence, horizon=1):
    """
    Generate multi-step forecasts by iteratively predicting the next value 
    and updating the input sequence.
    
    For simplicity, we assume that for the non-target features,
    the most recent values are repeated.
    """
    seq = initial_sequence.copy()  # shape: (seq_length, features)
    forecasts = []
    for _ in range(horizon):
        # Predict next value. Reshape to (1, seq_length, features)
        pred = model.predict(seq[np.newaxis, ...])
        # For confidence, we could also run MC dropout here.
        # Take the predicted revenue (we assume index 2 holds revenue).
        forecasts.append(pred[0, 0])
        # For the next step, update the sequence:
        # Create a new row by keeping last values for other features and
        # inserting the new predicted revenue.
        # Here we simply take the last row's other features (Historical_Sales, Customer_Trends_Score, Sales_Channel)
        last_row = seq[-1].copy()
        # Update revenue in last_row with predicted value.
        last_row[2] = pred[0, 0]
        # Append this new row and drop the oldest row.
        seq = np.vstack((seq[1:], last_row))
    return np.array(forecasts)

# --- Monte Carlo Dropout for Confidence ---
def mc_dropout_prediction(X, n_iter=30):
    preds = []
    for _ in range(n_iter):
        # Call model in training mode so dropout is active.
        pred = model(X, training=True)
        preds.append(pred.numpy())
    preds = np.array(preds)  # shape: (n_iter, batch_size, 1)
    mean_pred = np.mean(preds, axis=0)
    std_pred = np.std(preds, axis=0)
    return mean_pred, std_pred

# --- Prediction Function ---
def predict_revenue(new_data, horizon=1, use_mc_dropout=False):
    try:
        X_new = preprocess_custom_data(new_data)
        if X_new is None or X_new.shape[0] == 0:
            return None, None
        
        # For single-step prediction (horizon==1), we predict on all sequences.
        if horizon == 1:
            if use_mc_dropout:
                mean_pred, std_pred = mc_dropout_prediction(X_new)
                predictions = mean_pred
                confidence = std_pred
            else:
                predictions = model.predict(X_new)
                confidence = None

            # Convert predictions to original scale.
            predictions_rescaled = scaler.inverse_transform(
                np.concatenate([predictions, np.zeros((predictions.shape[0], 3))], axis=1)
            )[:, 2]
            return predictions_rescaled, confidence

        else:
            # For multi-step predictions, use the last sequence in X_new as initial input.
            initial_sequence = X_new[-1]
            multi_preds = multi_step_forecast(initial_sequence, horizon=horizon)
            # Rescale the multi-step predictions.
            # Build a dummy array to inverse transform: place predictions in index 2, zeros elsewhere.
            dummy = np.concatenate([multi_preds.reshape(-1, 1), np.zeros((horizon, 3))], axis=1)
            predictions_rescaled = scaler.inverse_transform(dummy)[:, 0]  # Adjust column index if needed.
            return predictions_rescaled, None
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return None, None

# --- Download Button Helper ---
def download_csv(dataframe, filename="predictions.csv"):
    csv = dataframe.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Predictions as CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# --- App UI ---
def sales_page():
    st.title("📈 Revenue Forecast Simulator")
    st.markdown("Predict future revenue based on historical sales data using AI/ML.")

    with st.expander("ℹ️ How it works"):
        st.markdown("""
        **Process:**
        - **Upload a CSV** or **enter data manually**.
        - See exploratory insights on the data.
        - Choose your forecast horizon (number of future periods).
        - Optionally, view a model confidence indicator using MC Dropout.
        - Download the predictions.
        """)
    
    # --- Data Input Section ---
    st.subheader("1. Upload Your Data (CSV) or Enter Manually")
    option = st.radio("Select Input Option", options=["CSV Upload", "Manual Input"])
    
    data = None
    if option == "CSV Upload":
        uploaded_file = st.file_uploader("Upload CSV file (with at least 24 rows)", type=["csv"])
        if uploaded_file is not None:
            try:
                data = pd.read_csv(uploaded_file)
                required_columns = ['Customer_ID', 'Historical_Sales', 'Customer_Trends_Score', 'Revenue', 'Sales_Channel']
                if all(col in data.columns for col in required_columns):
                    st.success("✅ CSV uploaded successfully.")
                    st.subheader("Exploratory Data Insights")
                    st.dataframe(data.describe())
                    st.bar_chart(data['Revenue'])
                else:
                    st.error(f"CSV must include these columns: {', '.join(required_columns)}")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
    else:
        st.subheader("Manual Data Entry")
        num_rows = st.number_input("Number of Time Steps (Rows)", min_value=24, value=24, step=1)
        customer_id = st.number_input("Customer ID", min_value=1, value=1001)
        historical_sales = st.number_input("Average Historical Sales", value=8500.0)
        customer_trends_score = st.number_input("Customer Trends Score (0–1)", min_value=0.0, max_value=1.0, value=0.82)
        revenue = st.number_input("Last Recorded Revenue", value=20000.0)
        sales_channel = st.selectbox("Sales Channel", options=["Retail", "Wholesale", "Direct"])
        data = pd.DataFrame({
            'Customer_ID': [customer_id] * num_rows,
            'Historical_Sales': [historical_sales] * num_rows,
            'Customer_Trends_Score': [customer_trends_score] * num_rows,
            'Revenue': [revenue] * num_rows,
            'Sales_Channel': [sales_channel] * num_rows
        })
        st.dataframe(data.head())
    
    # --- Forecast Horizon & Confidence Options ---
    st.subheader("2. Forecast Settings")
    horizon = st.slider("Forecast Horizon (Future Time Steps)", min_value=1, max_value=10, value=1, step=1)
    use_confidence = st.checkbox("Show Model Confidence Indicator (MC Dropout)", value=False)
    
    # --- Predict Button ---
    if st.button("🔍 Predict Revenue"):
        if data is not None:
            prediction, confidence = predict_revenue(data, horizon=horizon, use_mc_dropout=use_confidence)
            if prediction is not None:
                st.success("✅ Forecast generated successfully!")
                
                if horizon == 1:
                    st.metric(label="Forecasted Revenue (Next Period)", value=f"${prediction[-1]:,.2f}")
                else:
                    st.markdown(f"**Forecast for the next {horizon} periods:**")
                    st.write(prediction)
                    
                # Plot forecast trend
                st.subheader("Forecast Trend")
                st.line_chart(prediction)
                
                # Show model confidence if enabled (only for horizon=1)
                if use_confidence and confidence is not None:
                    # Here, we assume confidence is an array aligned with predictions.
                    # We display average standard deviation.
                    avg_conf = np.mean(confidence)
                    st.info(f"Model Confidence (Mean Std. Deviation): {avg_conf:.2f}")
                
                # Calculate basic insight
                last_actual = data.iloc[-1]['Revenue']
                delta = prediction[-1] - last_actual
                st.subheader("Business Insight")
                if delta > 0:
                    st.markdown(f"📈 Revenue is expected to increase by **${delta:,.2f}**.")
                elif delta < 0:
                    st.markdown(f"📉 Revenue is expected to decrease by **${abs(delta):,.2f}**. Consider reviewing your strategy.")
                else:
                    st.markdown("🔁 No significant change in revenue forecast.")
                
                # --- Provide Download Option ---
                result_df = pd.DataFrame({
                    "Forecasted_Revenue": prediction
                })
                download_csv(result_df, filename="predicted_revenue.csv")
            else:
                st.error("🚫 Prediction failed. Check your input data.")
        else:
            st.error("🚫 No data provided. Please upload a CSV or enter data manually.")

if __name__ == "__main__":
    sales_page()
