# ERP Simulation WebApp – Module-wise Summary

## 1. Home
- Displays key metrics and performance KPIs  
- Shows pending approvals and system notifications  
- Integrated support chat interface

## 2. Sales Management
- Enter and manage sales orders  
- Generate customer invoices as downloadable PDFs  
- Sales dashboard with interactive visualizations

## 3. Product Management
- Create, update, and delete product records  
- Monitor stock levels and movement  
- View product-wise sales trends

## 4. Forecasting & Predictions
- Revenue prediction using LSTM time series model  
- Select forecast horizon (days/weeks)  
- Option to download predictions and view error metrics

## 5. Vendor Approval Prediction
- Uses XGBoost classifier for vendor approval decisions  
- Displays prediction score and classification result  
- Highlights contributing features for transparency

## 6. Invoice Intelligence
- Upload invoice images for OCR processing (Tesseract)  
- Extracts and validates fields using regex + database match  
- Highlights mismatches for reconciliation

## 7. Insights Dashboard
- Aggregated analytics on sales, products, vendors  
- Filter by category, date range, or status  
- Exportable charts and data summaries

## 8. File Encryption
- Upload and encrypt/decrypt files using AES or DES  
- User selects encryption method and provides keys  
- Optional time-limited access settings

## 9. ERP Support Chatbot
- Natural language help for ERP and module queries  
- Trained on SAP and ERP documentation  
- Available from any page as floating assistant
