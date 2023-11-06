# Sets required env vars 
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project) 
export DATA_SOURCE_TYPE=BIG_QUERY
export PARTNER_TYPE=WHATSAPP
export BQ_DATASET_NAME=wci
export API_KEY="My_Key"
export PROTOCOL_MESSAGE="Chat ID"
export WELCOME_MESSAGE="Hello, World"
export STATS_OPTIN=yes
export ECL_ENABLED=false
export BQ_PENDING_LEAD_TABLE="${GOOGLE_CLOUD_PROJECT}.${BQ_DATASET_NAME}.pending_leads"
export BQ_LEAD_TABLE="${GOOGLE_CLOUD_PROJECT}.${BQ_DATASET_NAME}.leads"
export BQ_CHAT_TABLE="${GOOGLE_CLOUD_PROJECT}.${BQ_DATASET_NAME}.chat_leads"

# Runs the solution locally
python3 app/main.py