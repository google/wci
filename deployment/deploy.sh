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
    start_message "Enabling required services (artifactregistry, cloud run)"
    gcloud services enable run.googleapis.com
    gcloud services enable artifactregistry.googleapis.com
}
function create_artifacts(){
    gcloud artifacts repositories create wci \
    --repository-format=docker \
    --location=$REGION \
    --description="WCI Repo"

    # Builds WCI image
    start_message "Builds WCI Image..."
    docker build ./ -t wci -f ./deployment/docker/Dockerfile
    docker tag wci $REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/wci/wci
    docker push $REGION-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/wci/wci
    echo 
}
function create_service_account() {
    start_message "Creating the service account ${SERVICE_ACCOUNT_NAME}..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name='Service Account for WCI use'
    # Add editor role to the service account
    gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
    --member "serviceAccount:${SERVICE_ACCOUNT}" \
    --role "roles/bigquery.admin"
    echo
}
function create_bq_dataset() {
    start_message "Creating dataset ${BQ_DATASET_NAME}..."
    bq --location=$BQ_LOCATION mk \
    --dataset \
    --description="BigQuery dataset for WCI" \
    --label=name:$BQ_DATASET_NAME \
    $GOOGLE_CLOUD_PROJECT:$BQ_DATASET_NAME
    echo
}
function create_bq_tables(){
    start_message "Creating WCI schema:chat_leads..."
    
    bq mk \
    --table \
    --description="BigQuery table for WCI" \
    $GOOGLE_CLOUD_PROJECT:$BQ_DATASET_NAME.chat_leads \
    sender:STRING,receiver:STRING,message:STRING,timestamp:TIMESTAMP
    echo

    start_message "Creating WCI schema:pending_leads..."
    bq mk \
    --table \
    --description="BigQuery table for WCI" \
    $GOOGLE_CLOUD_PROJECT:$BQ_DATASET_NAME.pending_leads \
    identifier:STRING,type:STRING,protocol:STRING,mapped:JSON,timestamp:TIMESTAMP
    echo

    start_message "Creating WCI schema:leads..."
    bq mk \
    --table \
    --description="BigQuery table for WCI" \
    $GOOGLE_CLOUD_PROJECT:$BQ_DATASET_NAME.leads \
    protocol:STRING,phone:STRING,timestamp:TIMESTAMP
    echo
}
function deploy_app(){
    echo "${bold}${text_green}To deploy, inform the following values:${reset}"

    echo -n "Type the API Key:"
    read -r API_KEY

    echo -n "Type the message to be sent with the protocol number (E.g. Your protocol is):"
    read -r PROTOCOL_MESSAGE

    echo -n "Type the message to be sent AFTER the protocol number (E.g. Your protocol is 98765432. Hello, Advertiser):"
    read -r WELCOME_MESSAGE

    echo -n "Optin to collect usage stats to improve the solution (E.g. yes/no):"
    read -r STATS_OPTIN

    cp ./app/app.yaml ./deployment/

    sed -i "s/{{GOOGLE_CLOUD_PROJECT}}/$GOOGLE_CLOUD_PROJECT/g" ./deployment/app.yaml
    sed -i "s/{{REGION}}/$REGION/g" ./deployment/app.yaml
    sed -i "s/{{SERVICE_ACCOUNT}}/${SERVICE_ACCOUNT}/g" ./deployment/app.yaml
    sed -i "s/{{BQ_DATASET_NAME}}/$BQ_DATASET_NAME/g" ./deployment/app.yaml
    sed -i "s/{{API_KEY}}/${API_KEY}/g" ./deployment/app.yaml
    sed -i "s/{{PROTOCOL_MESSAGE}}/${PROTOCOL_MESSAGE}/g" ./deployment/app.yaml
    sed -i "s/{{WELCOME_MESSAGE}}/${WELCOME_MESSAGE}/g" ./deployment/app.yaml
    sed -i "s/{{STATS_OPTIN}}/${STATS_OPTIN}/g" ./deployment/app.yaml
    echo

    # Create repository for docker image
    create_artifacts
    echo    

    # Deploys the service 
    start_message "Deploying WCI Service..."
    gcloud run services replace ./deployment/app.yaml
    echo

    echo "✅ ${bold}${text_green} Service deployed${reset}"
    echo

    start_message "Making WCI accessible..."
    gcloud run services add-iam-policy-binding wci --region $REGION \
    --member="allUsers" \
    --role="roles/run.invoker"
    echo

    ENDPOINT="$(gcloud run services list | grep -oP '(http|https)://wci(.*)')"
    echo "${bold}${text_yellow}NEXT STEPS: To finalize, set your account's webhook to${reset}"
    echo "${bold}Callback URL: ${text_yellow}${ENDPOINT}/webhook-wci${reset}"
    echo "${bold}Verify token: ${text_yellow}${API_KEY}${reset}"
    echo "${bold}Lead URL: ${text_yellow}${ENDPOINT}/webhook${reset}"
    echo
}
function init() {
    echo
    echo "${bold}┌────────────────┐${reset}"
    echo "${bold}│ WCI Deployment │${reset}"
    echo "${bold}└────────────────┘${reset}"
    echo
    echo "${bold}${text_red}This is not an officially supported Google product.${reset}"
    echo "${bold}WCI will be deployed in the Google Cloud project ${text_green}${GOOGLE_CLOUD_PROJECT}${bold}${reset}"
    echo
    if [ -z "${CLOUD_SHELL}" ]; then
        echo "${bold}${text_yellow}WARNING! You are not running this script from the Google Cloud Shell environment.${reset}"
        echo
    fi

    # Get parameters
    if [ -z "${GOOGLE_CLOUD_PROJECT}" ]; then
        GOOGLE_CLOUD_PROJECT="$(gcloud config get-value project)"
    fi
    
    #Collects variables
    BQ_DATASET_NAME=${BQ_DATASET_NAME:="wci"}
    BQ_LOCATION=${BQ_DATASET_LOCATION:="US"}
    REGION=${REGION:="us-central1"}
    SERVICE_ACCOUNT_NAME=${SERVICE_ACCOUNT_NAME:="wci-runner"}
    SERVICE_ACCOUNT="${SERVICE_ACCOUNT_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com"

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
        
        create_bq_tables
        deploy_app
        echo "✅ ${bold}${text_green} Deployment Done!${reset}"
        echo
    fi
}

init