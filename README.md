# pro_con_service
Service for extracting pros and cons from reviews

## Machine Preparation
Machine: Ubuntu 20.04 16GB Ram.\
Remember to open the TCP port `8001` to let the server
listen for incoming REST request.

Update the system, install pip, and venv:

    sudo apt update
    sudo apt upgrade
    sudo apt install python3-pip
    sudo apt-get install python3-venv
    
Create a and activate a virtual environment:

    python3 -m venv procon_project
    source procon_project/bin/activate
    
## Pull code and prepare the DB
Pull the ProCon code and install the requirements.
Remember to run everything within the environment you created above
(remember public/private ssh keys for github).

For spaCy, please install the english medium model:

    `python -m spacy download en_core_web_md`

## Run the service
To run the service, it should be enough to run the script `run_server.sh`.
This will start the server listening on the port `8001`.
You can then use `Postman` or other tools to send REST API request
to the server.

## Endpoints
#### Amazon Product Pro-Con
Post request

`http://3.22.185.47:8001/pro_con?key=`

Params

    `key: oogway_test`
    
Body

`{
  "url": "https://www.amazon.com/Celestron-71198-Cometron-Binoculars-Black/dp/B00DV6SI3Q?ref_=Oct_DLandingS_D_1318bab5_61&smid=ATVPDKIKX0DER&th=1"
 }`

#### Restaurant Pro-Con
Post request

`http://3.22.185.47:8001/pro_con_restaurant?key=`

Params

    `key: oogway_test`
    
Body

`{
    "restaurant_name": "Barcelona Wine Bar South End",
    "city": "Boston",
    "max_num_reviews": 10
}`
