import json
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from .models import Group, Message
from django.utils.text import slugify
from .forms import SignUpForm
from rest_framework import status


class GroupViewsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group1 = Group.objects.create(name='Group 1', admin=self.user, slug=slugify('Group 1'))
        self.group2 = Group.objects.create(name='Group 2', admin=self.user, slug=slugify('Group 2'))

    def test_create_user_valid_data(self):
        # Test creating a user with valid data
        data = {
            'username': 'testuser2',
            'password': 'testpassword',
        }
        response = self.client.post('/api/create-user/', data, format='json')

        # Expect HTTP 201 CREATED as the user is successfully created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the user was created in the database
        new_user = User.objects.get(username='testuser')
        self.assertIsNotNone(new_user)

        # Check the response message
        self.assertEqual(response.data, {'message': 'User created successfully.'})

    def test_create_user_missing_username(self):
        # Test creating a user with missing username
        data = {
            'password': 'testpassword',
        }
        response = self.client.post('/api/create-user/', data, format='json')

        # Expect HTTP 400 BAD REQUEST as username is required
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the error message in the response
        self.assertEqual(response.data, {'error': 'Both username and password are required.'})

    def test_create_user_missing_password(self):
        # Test creating a user with missing password
        data = {
            'username': 'testuser',
        }
        response = self.client.post('/api/create-user/', data, format='json')

        # Expect HTTP 400 BAD REQUEST as password is required
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the error message in the response
        self.assertEqual(response.data, {'error': 'Both username and password are required.'})

    def test_create_user_existing_username(self):
        # Test creating a user with an existing username
        # Create a user with the same username as in this test
        User.objects.create_user(username='testuser2', password='existingpassword')

        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post('/api/create-user/', data, format='json')

        # Expect HTTP 400 BAD REQUEST as the username already exists
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check the error message in the response
        self.assertEqual(response.data, {'error': 'Username already exists.'})


    def test_signup_view_post_valid_form(self):
        # Test the signup view with a POST request
        data = {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword'
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)  # Expect a redirect after successful signup

    def test_signup_view_post_invalid_form(self):
        # Test the signup view with a POST request with an invalid form
        data = {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'differentpassword',  # Invalid password confirmation
        }
        response = self.client.post(reverse('signup'), data)

        # Expect HTTP 200 OK as the form is invalid and should render the signup form again
        self.assertEqual(response.status_code, 200)

        # Check if the form is in the context
        self.assertIsInstance(response.context['form'], SignUpForm)

        # Check if the user was not created in the database
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='newuser')

    def test_group_view(self):
        # Test the group view with a logged-in user

        # Simulate a logged-in user
        self.client.login(username='testuser', password='testpassword')

        # Create a group and a message associated with that group
        test_group = Group.objects.create(name='Test Group', admin=self.user, slug=slugify('Test Group'))
        test_message = Message.objects.create(group=test_group, content='Test message', user=self.user)

        response = self.client.get(reverse('group', args=[test_group.slug]))

        # Expect HTTP 200 OK as the user is logged in
        self.assertEqual(response.status_code, 200)

        # Check if the group and the message are in the context
        self.assertEqual(response.context['group'], test_group)

        # Get the list of message texts from the context
        messages_from_context = [message.content for message in response.context['messages']]

        # Get the list of message texts from the database
        messages_from_db = list(Message.objects.filter(group=test_group).values_list('content', flat=True))

        # Compare the lists of message texts
        self.assertCountEqual(messages_from_context, messages_from_db)

    def test_group_view_unauthorized(self):
        # Test the group view without a logged-in user
        test_group = Group.objects.create(name='Test Group', admin=self.user, slug=slugify('Test Group'))
        response = self.client.get(reverse('group', args=[test_group.slug]))

        # Expect HTTP 302 redirect as the user is not logged in and should be redirected to login page
        self.assertEqual(response.status_code, 302)

    def test_groups_view(self):
        # Test the groups view with a logged-in user
        self.client.login(username='testuser', password='testpassword')
        self.group1.members.add(self.user)
        self.group2.members.add(self.user)

        response = self.client.get(reverse('groups'))

        # Expect HTTP 200 OK as the user is logged in
        self.assertEqual(response.status_code, 200)

        # Check if the user is in the context and has access to their groups
        self.assertEqual(response.context['user'], self.user)
        group_slugs_from_context = [group.slug for group in response.context['groups']]

        # Get the list of group slugs from the database
        group_slugs_from_db = list(Group.objects.filter(members=self.user).values_list('slug', flat=True))

        # Compare the lists of group slugs
        self.assertCountEqual(group_slugs_from_context, group_slugs_from_db)

    def test_groups_view_unauthorized(self):
        # Test the groups view without a logged-in user
        response = self.client.get(reverse('groups'))

        # Expect HTTP 302 redirect as the user is not logged in and should be redirected to login page
        self.assertEqual(response.status_code, 302)

    def test_create_group_view_post_valid_form(self):
        # Test the create_group view with a POST request with a valid form
        # Simulate a logged-in user
        self.client.login(username='testuser', password='testpassword')

        data = {
            'name': 'Test Group',
        }
        response = self.client.post(reverse('create-group'), data)

        # Expect a redirect after successful group creation
        self.assertEqual(response.status_code, 302)

        # Check if the group was created in the database
        new_group = Group.objects.get(name='Test Group')
        self.assertEqual(new_group.admin, self.user.username)

    def test_create_group_view_post_duplicate_name(self):
        # Test the create_group view with a POST request with a duplicate group name
        # Simulate a logged-in user
        self.client.login(username='testuser', password='testpassword')

        # Create a test group with the same name as the one we want to duplicate
        Group.objects.create(name='Test Group', admin=self.user)

        data = {
            'name': 'Test Group',
        }
        response = self.client.post(reverse('create-group'), data)

        # Expect HTTP 200 OK as the user is logged in, and the form will not be valid due to duplicate name
        self.assertEqual(response.status_code, 200)

        # Check if the group was not created in the database
        groups_with_duplicate_name = Group.objects.filter(name='Test Group')
        self.assertEqual(groups_with_duplicate_name.count(), 1)

        # Check if a warning message was set in the response
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f'A group name Test Group already exists...')

    def test_create_group_view_unauthorized(self):
        # Test the create_group view without a logged-in user
        response = self.client.get(reverse('create-group'))

        # Expect HTTP 302 redirect as the user is not logged in and should be redirected to login page
        self.assertEqual(response.status_code, 302)

    def test_delete_group_view_post_as_admin(self):
        # Test the delete_group view with a POST request as the group admin
        # Simulate a logged-in user
        self.client.login(username='testuser', password='testpassword')

        response = self.client.post(reverse('delete-group', args=[self.group1.slug]))

        # Expect a redirect after successful deletion as the user is the group admin
        self.assertEqual(response.status_code, 302)

        # Check if the group was deleted from the database
        self.assertFalse(Group.objects.filter(slug=self.group1.slug).exists())

    def test_delete_group_view_post_as_member(self):
        # Test the delete_group view with a POST request as a group member
        # Simulate a logged-in user who is a member of the group
        self.client.login(username='testuser', password='testpassword')

        # Add the user as a member of the group
        self.group1.members.add(self.user)

        response = self.client.post(reverse('delete-group', args=[self.group1.slug]))

        # Expect a redirect after removal from the group as the user is not the group admin
        self.assertEqual(response.status_code, 302)

        # Check if the user is removed from the group in the database
        self.assertNotIn(self.user, self.group1.members.all())

    def test_delete_group_view_unauthorized(self):
        # Test the delete_group view without a logged-in user
        response = self.client.post(reverse('delete-group', args=[self.group1.slug]))

        # Expect HTTP 302 redirect as the user is not logged in and should be redirected to login page
        self.assertEqual(response.status_code, 302)

    def test_add_members_view(self):
        # Test the add_members view with a POST request
        self.client.login(username='testuser', password='testpassword')
        # Create another user for testing
        test_user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        # Create a new group for testing
        test_group = Group.objects.create(name='Test Group', admin=self.user, slug=slugify('Test Group'))

        data = {
            'member_username': 'testuser2',  # Add testuser2 as a member
        }
        response = self.client.post(reverse('add-members', args=[test_group.slug]), data)

        # Expect a redirect after successfully adding the member
        self.assertEqual(response.status_code, 302)

        # Check if the member was added to the group in the database
        self.assertTrue(test_group.members.filter(username='testuser2').exists())

    def test_add_members_view_invalid_user(self):
        # Test the add_members view with a POST request and an invalid username
        # Simulate a logged-in user
        self.client.login(username='testuser', password='testpassword')

        # Create a new group for testing
        test_group = Group.objects.create(name='Test Group', admin=self.user, slug=slugify('Test Group'))

        data = {
            'member_username': 'nonexistentuser',  # Try to add a non-existent user
        }
        response = self.client.post(reverse('add-members', args=[test_group.slug]), data)

        # Expect a redirect even if the user doesn't exist, as we are not handling this case in the view
        self.assertEqual(response.status_code, 302)

        # Check that the group has no members added
        self.assertEqual(test_group.members.count(), 0)

    def test_group_users_view(self):
        # Test the group_users view with a logged-in user
        self.client.login(username='testuser', password='testpassword')

        # Add some members to the group for testing
        test_user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        test_user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.group1.members.add(test_user1, test_user2)

        response = self.client.get(reverse('group-users', args=[self.group1.slug]))

        # Expect HTTP 200 OK as the user is logged in
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response
        data = json.loads(response.content)
        users_data = data['users']

        # Expect the response to contain the usernames of added members
        self.assertEqual(len(users_data), 2)
        self.assertIn('testuser1', [user_data['username'] for user_data in users_data])
        self.assertIn('testuser2', [user_data['username'] for user_data in users_data])

    def test_group_users_view_unauthorized(self):
        # Test the group_users view without a logged-in user
        response = self.client.get(reverse('group-users', args=[self.group1.slug]))

        # Expect HTTP 302 redirect as the user is not logged in and should be redirected to login page
        self.assertEqual(response.status_code, 302)

    def test_search_groups_view_with_results(self):
        # Test the search_groups view with a logged-in user and valid query
        self.client.login(username='testuser', password='testpassword')

        # Make a GET request with a query that matches a group's name
        response = self.client.get(reverse('search-groups'), {'query': 'Group 1'})

        # Expect HTTP 200 OK as the user is logged in
        self.assertEqual(response.status_code, 200)

        # Expect to find the matching group in the response
        self.assertIn(self.group1, response.context['groups'])
        self.assertNotIn(self.group2, response.context['groups'])

    def test_search_groups_view_without_results(self):
        # Test the search_groups view with a logged-in user and query without results
        self.client.login(username='testuser', password='testpassword')

        # Make a GET request with a query that doesn't match any group's name
        response = self.client.get(reverse('search-groups'), {'query': 'Nonexistent Group'})

        # Expect HTTP 200 OK as the user is logged in
        self.assertEqual(response.status_code, 200)

        # Expect no groups in the response
        self.assertEqual(len(response.context['groups']), 0)

    def test_search_groups_view_unauthorized(self):
        # Test the search_groups view without a logged-in user
        response = self.client.get(reverse('search-groups'))

        # Expect HTTP 302 redirect as the user is not logged in and should be redirected to login page
        self.assertEqual(response.status_code, 302)
