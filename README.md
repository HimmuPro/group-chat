# Group Chat 
This is Django based group chat application which is use to manage groups (to create group, delete group, add members in a group, view members of a group).



# Features
Some of the key features of this applications include:

* Admin API to add users.
* If user is Logged In then he/she able to see groups which is created by the user itself or if the user is the member of any group.
* If user open any group for chat, then he/she can delete the group,
  * if user is the admin/owner of that group then the group will be deleted permanently.
  * if user is the member of that group but not the admin/owner then the group will be deleted from their profile only.
* User can view the members of the group.
* User can add members to the group, when user wants to add member in a group then the dropdown with the users which is not the part of the group can be visible.
* User can sends messages to the group, the owner of the message can view their messages on the right part of the chat window, rest users message will be visible to the left part of the window.
* User can like the messages multiple time, the likes count will increased on the realtime basis. (Can update like/unlike function in future)
* After LogIn the user can see 2 options,
  * Create group - user can create group by adding group name.
  * Search group - user can search group by providing group name.

## Project Structure

The project structure is organized as follows:

```
└── group_chat/
    ├── group/
    │   ├── templates/
    │   │   ├── add_members.html
    │   │   ├── base.html
    │   │   ├── create_group.html
    │   │   ├── delete_group.html
    │   │   ├── group.html
    │   │   ├── groups.html
    │   │   ├── home.html
    │   │   ├── login.html
    │   │   ├── search_group.html
    │   │   └── signup.html
    │   ├── admin.py
    │   ├── apps.py
    │   ├── consumers.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── routing.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── views.py
    ├── group_chat/
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── manage.py
    ├── README.md
    └── requirements.txt
```

## Getting started

To run the application, follow these steps:

1. Clone the repository:

   ```shell
   git clone https://github.com/HimmuPro/chatting.git
   ```

2. Navigate to the project directory:

   ```shell
   cd group_chat
   ```

3. Create a virtual environment:

   ```shell
   python3 -m venv venv
   ```

4. Activate the virtual environment:

   - On macOS and Linux:

     ```shell
     source venv/bin/activate
     ```

   - On Windows:

     ```shell
     venv\Scripts\activate
     ```

5. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```

6. Configuration:
    
   - Run makemigraions and migrate command to reflect models changes in database (used db.sqlite):
     ```shell
     python manage.py makemigrations
     python manage.py migrate
     ```
   
   - Create superuser to manage uses data,
     ```shell
     python manage.py createsuperuser
     ```
     
7. Run the application:

   ```shell
   python manage.py runserver
   ```

   The application will start running on `http://localhost:8000`.


## Admin API's 

   * To create user - ```http://localhost:8000/api/create-user/```
   * To edit user - ```http://localhost:8000/api/edit-user/<username>/```

## Application Flow

1. Home page ```http://localhost:8000```
2. After LogIn ```http://localhost:8000/groups/``` will display the groups if user created any or if the user is the member of any group.
3. ```http://localhost:8000/groups/search/?query=<group_name>``` will redirect to the page where search results found.
4. ```http://localhost:8000/groups/create/``` will redirect to page where group name is required to enter in the form to create a group.
5. ```http://localhost:8000/groups/<group_name>/``` will open the group where messages (if any) can be seen also here three buttons will display
   (i) to delete group, (ii) to view all members, and (iii) to add member.
6. ```http://localhost:8000/groups/<group_name>/add-members/``` will open form to select member name to add in the group

## To run testcases

   ```shell
   python manage.py test
   ```

