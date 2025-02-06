import streamlit as st
import datetime
import uuid
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Load Google Ads API client


# # Load Google Ads API client from a specific path (D drive in this case)
# GOOGLE_ADS_CLIENT = GoogleAdsClient.load_from_storage(r"google-ads.yaml")


def get_customer_id():
    """Retrieves the Customer ID from google-ads.yaml configuration file."""
    try:
        # customer_id = GOOGLE_ADS_CLIENT.login_customer_id
        if not customer_id:
            raise ValueError("❌ No Customer ID found in google-ads.yaml.")
        # return str(customer_id)  
    except Exception as e:
        print(f"❌ Error retrieving Customer ID from google-ads.yaml: {e}")
        return None


# Streamlit App Title
st.title("🤖 AI-Powered Google Ads Campaign Creator")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.campaign_details = {}

# Define questions and process responses
QUESTIONS = [
    "What is the name of your campaign?",
    "What is your daily budget in INR?",
    "What type of advertising do you want? (Search, Display, Shopping)?",
    "Do you want to enable Google Search Partners? (yes or no)?",
    "What is your campaign start date? (YYYY-MM-DD)?",
    "What is your campaign end date? (YYYY-MM-DD)?"
]

def validate_date_format(date_str):
    """Checks if input is a valid YYYY-MM-DD date format."""
    try:
        datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_future_date(date_str):
    """Ensures the given date is in the future."""
    input_date = datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    return input_date >= datetime.date.today()

def validate_date_order(start_date, end_date):
    """Ensures Start Date is before End Date."""
    return datetime.datetime.strptime(start_date, "%Y-%m-%d") < datetime.datetime.strptime(end_date, "%Y-%m-%d")

def process_campaign_questions(user_input):
    """Handles campaign questions and ensures valid responses."""
    step = st.session_state.step
    campaign_details = st.session_state.campaign_details

    if step == 1:
        campaign_details["Campaign Name"] = user_input
    elif step == 2:
        if not user_input.replace('.', '', 1).isdigit():
            return "❌ Invalid budget. Please enter a numeric value in INR."
        campaign_details["Daily Budget"] = f"₹{user_input}"
    elif step == 3:
        if user_input.lower() not in ["search", "display", "shopping"]:
            return "❌ Invalid advertising type. Please enter: Search, Display, or Shopping."
        campaign_details["Advertising Type"] = user_input.capitalize()
    elif step == 4:
        if user_input.lower() not in ["yes", "no"]:
            return "❌ Invalid response. Please enter: yes or no."
        campaign_details["Google Search Partners"] = "Enabled" if user_input.lower() == "yes" else "Disabled"
    elif step == 5:
        if not validate_date_format(user_input):
            return "❌ Invalid date format. Please enter Start Date in YYYY-MM-DD format."
        if not validate_future_date(user_input):
            return "❌ Start Date cannot be in the past. Please enter a future date."
        campaign_details["Start Date"] = user_input
    elif step == 6:
        if not validate_date_format(user_input):
            return "❌ Invalid date format. Please enter End Date in YYYY-MM-DD format."
        if not validate_future_date(user_input):
            return "❌ End Date cannot be in the past. Please enter a future date."
        if not validate_date_order(campaign_details["Start Date"], user_input):
            return "❌ End Date must be after Start Date. Please enter a valid End Date."
        campaign_details["End Date"] = user_input

    st.session_state.campaign_details = campaign_details

    if step < len(QUESTIONS):
        st.session_state.step += 1
        return QUESTIONS[st.session_state.step - 1]
    else:
        return review_campaign(campaign_details)

def review_campaign(campaign_details):
    """Summarizes the campaign details and asks for confirmation before creation."""
    summary = (
        f"📋 Here is your campaign summary:\n\n"
        f"📌 Campaign Name: {campaign_details.get('Campaign Name', 'N/A')}\n"
        f"💰 Daily Budget: {campaign_details.get('Daily Budget', 'N/A')}\n"
        f"🎯 Advertising Type: {campaign_details.get('Advertising Type', 'N/A')}\n"
        f"🔍 Google Search Partners: {campaign_details.get('Google Search Partners', 'N/A')}\n"
        f"📅 Start Date: {campaign_details.get('Start Date', 'N/A')}\n"
        f"⏳ End Date: {campaign_details.get('End Date', 'N/A')}\n\n"
        f"✅ Does everything look correct? Type 'yes' to confirm!"
    )

    st.session_state.step = "confirm"  # Move to confirmation step
    return summary


# def create_google_ads_campaign(client: GoogleAdsClient, customer_id: str, campaign_details):
#     """Creates a Google Ads campaign with a budget and applies the correct settings."""
#     try:
#         campaign_budget_service = client.get_service("CampaignBudgetService")
#         campaign_service = client.get_service("CampaignService")

#         # Create Campaign Budget
#         campaign_budget_operation = client.get_type("CampaignBudgetOperation")
#         campaign_budget = campaign_budget_operation.create
#         campaign_budget.name = f"Budget for {campaign_details['Campaign Name']} {uuid.uuid4()}"
#         campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
#         campaign_budget.amount_micros = int(float(campaign_details["Daily Budget"].replace("₹", "")) * 1_000_000)
#         campaign_budget.explicitly_shared = False

#         campaign_budget_response = campaign_budget_service.mutate_campaign_budgets(
#             customer_id=customer_id, operations=[campaign_budget_operation]
#         )
#         budget_resource_name = campaign_budget_response.results[0].resource_name

#         # Create Campaign
#         campaign_operation = client.get_type("CampaignOperation")
#         campaign = campaign_operation.create
#         campaign.name = f"{campaign_details['Campaign Name']} {uuid.uuid4()}"
#         campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
#         campaign.status = client.enums.CampaignStatusEnum.PAUSED
#         campaign.campaign_budget = budget_resource_name

#         campaign.network_settings.target_google_search = True
#         campaign.network_settings.target_search_network = True
#         campaign.network_settings.target_partner_search_network = False
#         campaign.network_settings.target_content_network = True

#         campaign.start_date = campaign_details["Start Date"].replace("-", "")
#         campaign.end_date = campaign_details["End Date"].replace("-", "")

#         campaign.manual_cpc = client.get_type("ManualCpc")

#         campaign_response = campaign_service.mutate_campaigns(
#             customer_id=customer_id, operations=[campaign_operation]
#         )

#         return campaign_response.results[0].resource_name

#     except GoogleAdsException as ex:
#         return f"❌ Failed to create campaign: {ex}"


# Streamlit logic for the chatbot
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.campaign_details = {}

# Display the current question
current_question = QUESTIONS[st.session_state.step - 1]
st.subheader(current_question)

# Input field for user response
user_input = st.text_input("💬 Your response:")

if user_input:
    response = process_campaign_questions(user_input)
    st.write(response)

    # Handle confirmation
    if st.session_state.step == "confirm":
        if user_input.lower() == "yes":
            # customer_id = get_customer_id()
            # campaign_details = st.session_state.campaign_details
            # campaign_id = create_google_ads_campaign(GOOGLE_ADS_CLIENT, customer_id, campaign_details)
            # if campaign_id:
            #     st.success(f"🎉 Campaign created successfully! 🎉 ")  #Campaign ID: {campaign_id}
            # else:
            #     st.error("❌ Failed to create campaign. Please try again.")
            st.success("done")
            st.session_state.step = 1  # Reset chatbot after creating the campaign
            st.session_state.campaign_details = {}
        elif user_input.lower() == "no":
            st.session_state.step = 1
            st.session_state.campaign_details = {}
            st.write("📝 What would you like to edit? Please enter a new response for any question.")
