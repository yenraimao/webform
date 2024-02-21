from flask import Flask, render_template, request
import logging
import requests

api_key = ""

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO,filemode='a')  # Log to a file named 'app.log'

# adds email address to mailing list 
def add_list_member(address, full_name):
    return requests.post(
        "https://api.mailgun.net/v3/lists/apitest@mg.pockey.pro/members",
        auth=('api', api_key),
        data={'subscribed': True,
              'address': address,
              'name': full_name,
              })

# validates email address entered in form
def get_validate(address):
    return requests.get(
        "https://api.mailgun.net/v4/address/validate",
        auth=("api", api_key),
        params={"address": address})

# Define a simple form class
class EmailForm:
    def __init__(self):
        self.email = ""
        self.full_name = ""

# Route for the home page
@app.route('/form', methods=['GET', 'POST'])
def home():
    form = EmailForm()
    error_message = None
    success_message = None

    if request.method == 'POST':
        form.email = request.form['email']
        form.full_name = request.form['full_name']
        try:
            # Use the email in an API call
            response = get_validate(form.email)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            if response.status_code == 200:
                api_data = response.json()
                result = api_data['result']
                address = api_data['address']
                # return API data
                if result == 'deliverable':
                    if add_list_member(address,form.full_name):
                        success_message = "Success: Your email has been submitted successfully!"
                    else:
                        logging.error(f"Failed API request for email: {form.email}, Error: {e}")
                        error_message = f"Error: {e}"
                # Log a successful API request
                logging.info(f"Successful API request for email: {form.email}")
        except requests.RequestException as e:
            # Log an unsuccessful API request
            logging.error(f"Failed API request for email: {form.email}, Error: {e}")
            error_message = f"Error: {e}"

    return render_template('index.html', form=form,error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)