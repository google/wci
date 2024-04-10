#!/bin/bash
# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

reset="$(tput sgr 0)"
bold="$(tput bold)"
text_red="$(tput setaf 1)"
text_yellow="$(tput setaf 3)"
text_green="$(tput setaf 2)"

# Sets defaults variables
BQ_DATASET_NAME=${BQ_DATASET_NAME:="wci_activator"}
BQ_LOCATION=${BQ_DATASET_LOCATION:="US"}
REGION=${REGION:="US"}
SERVICE_ACCOUNT_NAME=${SERVICE_ACCOUNT_NAME:="wci-activator-runner"}
SERVICE_ACCOUNT="${SERVICE_ACCOUNT_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"

function start_message() {
    echo "☑️  ${bold}${text_green}$1${reset}"
}
function ask() {
    while true; do
    read -r -p "${BOLD}${1:-Continue?} : ${NOFORMAT}"
    case ${REPLY:0:1} in
        [yY]) return 0 ;;
        [nN]) return 1 ;;
        *) echo "Please answer yes or no."
    esac
    done
}
function enable_services(){
    start_message "Enabling required services (bq transfer, vertex api)"

    gcloud services enable bigquerydatatransfer.googleapis.com
    gcloud services enable aiplatform.googleapis.com
}
function create_service_account() {
    start_message "Creating the service account ${SERVICE_ACCOUNT_NAME}..."

    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name='Service Account for WCI Activator use'
    # Add editor role to the service account
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member "serviceAccount:${SERVICE_ACCOUNT}" \
    --role "roles/bigquery.admin" \
    --role "roles/aiplatform.admin"
    echo
}
function create_bq_dataset() {
    start_message "Creating dataset ${BQ_DATASET_NAME}..."
    
    bq --location=$BQ_LOCATION mk \
    --dataset \
    --description="BigQuery dataset for WCI Activator" \
    --label=name:$BQ_DATASET_NAME \
    $GOOGLE_CLOUD_PROJECT:$BQ_DATASET_NAME
    echo
}
function create_bq_tables(){
    start_message "Creating WCI Activator schema: topics_clustering..."
    
    bq mk \
    --table \
    --time_partitioning_type DAY \
    --description="BigQuery table for WCI Activator" \
    $GOOGLE_CLOUD_PROJECT:$BQ_DATASET_NAME.topics_clustering \
    topic:STRING,predicted_at:TIMESTAMP,chat_id:STRING,prompt:STRING,last_message_at:TIMESTAMP
    echo

    start_message "Creating WCI Activator schema: sentiment_analysis..."
    bq mk \
    --table \
    --time_partitioning_type DAY \
    --description="BigQuery table for WCI" \
    $GOOGLE_CLOUD_PROJECT:$BQ_DATASET_NAME.sentiment_analysis \
    sentiment:STRING,predicted_at:TIMESTAMP,chat_id:STRING,prompt:STRING,last_message_at:TIMESTAMP
    echo
}
function create_bq_connection(){
    start_message "Creating WCI Activator bq connection..."

    bq mk --connection --location=$REGION --project_id=$GOOGLE_CLOUD_PROJECT --connection_type=CLOUD_RESOURCE wci_activator-connection
    
}
function create_bq_model(){
    start_message "Creating WCI Activator model..."

    bq query --use_legacy_sql=false \
    "CREATE OR REPLACE MODEL
            \`$GOOGLE_CLOUD_PROJECT.$BQ_DATASET_NAME.gemini-pro\`
        REMOTE WITH CONNECTION 
            \`$GOOGLE_CLOUD_PROJECT.$REGION.wci_activator-connection\` 
        OPTIONS(ENDPOINT = 'gemini-pro')" 

}
function create_scheduled_topics_clustering(){
     start_message "Creating WCI Activator scheduled query: topics_clustering..."
  
    bq query \
    --use_legacy_sql=false \
    --destination_table=$BQ_DATASET_NAME.topics_clustering \
    --project_id=$GOOGLE_CLOUD_PROJECT \
    --display_name='wci activactor: topics_clustering' \
    --schedule='everyday 02:00' \
    --append_table=true \
    "$(envsubst '${GOOGLE_CLOUD_PROJECT}','{$BQ_DATASET_NAME}' < run_topics_clustering.sql)" 

}
function create_scheduled_sentiment_analysis(){
     start_message "Creating WCI Activator scheduled query: sentiment_analysis..."

    QUERY="$(envsubst '${GOOGLE_CLOUD_PROJECT}','{$BQ_DATASET_NAME}' < run_sentiment_analysis.sql)" 
     
    bq query \
    --use_legacy_sql=false \
    --project_id=$GOOGLE_CLOUD_PROJECT \
    --destination_table=$BQ_DATASET_NAME.sentiment_analysis \
    --display_name='wci activactor: sentiment_analysis' \
    --schedule='everyday 03:00' \
    --append_table=true \
    $QUERY

}

function init() {

    # Initiates deployment
    echo
    echo "${bold}┌──────────────────────────┐${reset}"
    echo "${bold}│ WCI Activator Deployment │${reset}"
    echo "${bold}└──────────────────────────┘${reset}"
    echo
    echo "${bold}${text_red}This is not an officially supported Google product.${reset}"
    echo "${bold}WCI will be deployed in the Google Cloud project ${text_green}${GOOGLE_CLOUD_PROJECT}${bold}${reset}"
    echo
    if [ -z "${CLOUD_SHELL}" ]; then
        echo "${bold}${text_yellow}WARNING! You are not running this script from the Google Cloud Shell environment.${reset}"
        echo
    fi

    # Confirm details
    echo
    echo "${bold}${text_green}Settings${reset}"
    echo "${bold}${text_green}──────────────────────────────────────────${reset}"
    echo "${bold}${text_green}Project ID: ${GOOGLE_CLOUD_PROJECT}${reset}"
    echo
    if ask "Continue?"; then
        
        echo
        enable_services
        
        echo
        EXISTING_SERVICE_ACCOUNT=$(gcloud iam service-accounts list --filter "email:${SERVICE_ACCOUNT_NAME}" --format="value(email)")
        if [ -z "${EXISTING_SERVICE_ACCOUNT}" ]; then
            create_service_account
        else
            echo
            echo "${text_yellow}INFO: Service account '${SERVICE_ACCOUNT_NAME}' already exists.${reset}"
            echo
        fi

        EXISTING_BQ_DATASET=$(bq ls --filter labels."name:${BQ_DATASET_NAME}")
        echo 'Dataset' $EXISTING_BQ_DATASET
        if [ -z "${EXISTING_BQ_DATASET}" ]; then
            create_bq_dataset
        else
            echo
            echo "${text_yellow}INFO: The dataset '${BQ_DATASET_NAME}' already exists."${reset}
            echo
        fi
        
        create_bq_connection
        create_bq_model
        create_scheduled_topics_clustering
        create_scheduled_sentiment_analysis

        echo "✅ ${bold}${text_green} Deployment Done!${reset}"

    fi
}


# Get parameters
if [ -z "${GOOGLE_CLOUD_PROJECT}" ]; then
    GOOGLE_CLOUD_PROJECT="$(gcloud config get-value project)"
fi

create_bq_tables
create_scheduled_sentiment_analysis