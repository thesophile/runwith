# runwith

 Run Python libraries online with ease

<!-- <img src="https://github.com/user-attachments/assets/6c703603-9cfc-483b-9f83-efb3fe6d9253" alt="screenshot" width="800" /> -->

<!-- ![manim_runwith](https://github.com/user-attachments/assets/b7d08c2e-db6f-4c07-beff-ac4c6b70f863) -->

<img width="1920" height="992" alt="Manim_Screenshot_cropped" src="https://github.com/user-attachments/assets/b96a1cc5-5c44-4e15-babf-34b76c1d225d" />

## What is runwith?
 Runwith is a web interface for running manim, but can be extended to any python library.
 It just runs a docker container with the manim image.
 I am currently running it in [runwith.cloud](https://runwith.cloud), enabling users to 
  - use manim without any installation.
  - run in mobile phones and tablets with low resources.
  - save the code to cloud and continue cross-device

 But I also hope it could grow to more than that. It could:
  - Make shareable code snippets
  - A library of manim code by users - publicy available, editable and executable.
  - Other popular libraries. Since we are running from a docker image, any library with an image can be run. Users can select a library and start coding.

 But, I can't do that alone. I need your help.
 **Please contribute**
 
 


## Local Installation

### Prerequisites

- **Python:** 3.10 and above. (otherwise django 5.1 wont work, which is needed for django_q2 to work)
- **Virtualenv** (optional but recommended)
- **Git**
- **pip**

 

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/thesophile/runwith.git 
   cd runwith
   ```
2. **Create a Virtual Environment:**

    ```
    python3 -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install Dependencies:**

    ```
    pip install -r requirements.txt
    ```

   **Install Docker**

    - [Debian](https://docs.docker.com/engine/install/debian/)
    
    - [Other systems](https://docs.docker.com/engine/install/)
  
   Pull manim image

    ```
     docker pull manimcommunity/manim
    ```

   Allow docker client to talk to docker

     ```
     sudo usermod -aG docker $USER
     newgrp docker
     ```

    Give permission for docker to write to media

     ```
     sudo chown -R 1000:1000 media
     ```
      
     >where its really
     >`sudo chown -R <container_UID>:<container_GID> /path/to/media`
     > here container_UID and container_GID are both `1000`. but you can check with:
     >```
     >docker run --rm manimcommunity/manim id
     >```

    
4. **Run Migrations and collecstatic:**

    ```
    python manage.py migrate
    ```

    ```
    python manage.py collectstatic --noinput
    ```

    Or just set Debug = True, no need for collecstatic

2. **Setup environment**

    - In dev/local environment, Put runwith_dev.env to the root directory (along with manage.py).
    It is currently placed at docs/runwith_dev.env
    
    OR export these directly:
    ```
    export DJANGO_ENV=dev # or prod
    export DJANGO_SECRET_KEY='your_secret_key'
    ```
    
5. **Start the Development Server:**

    schedule ping_cluster 

    (to detect if qcluster is running)

    ```
    python manage.py create_heartbeat
    ```
    start qcluster
    ```
    python manage.py qcluster
    ```
    start server
    ```
    python manage.py runserver
    ```

## Tech Stack

- Python
- Django
- Docker
- Postgresql
- DjangoQ

## License
GNU Affero General Public License v3.0

## Contributing

We still have to
- Fix Save/Open workflow
- Make Code shareable
- Make a Library of user generated code.
- Extend to other libraries, Since we are using docker image of manim, we can replace that with any library. I am thinking of a dropdown to select a library to run.

You are welcome to open a pull request









