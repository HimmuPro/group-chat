import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import GroupForm
from django.contrib import messages
from .models import Group, Message
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import SignUpForm
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def create_user(request):
    """
    API endpoint to create a new user.

    This view allows users to register by providing a unique username and password in the request data.
    If the provided username or password is missing, it will return a 400 Bad Request error.
    If the username is already taken, it will return a 400 Bad Request error.
    If the username is available and the password is provided, it will create a new user with the given
    username and password, and return a 201 Created response with a success message.

    Parameters:
        request (HttpRequest): The HTTP request object containing the user's data.

    Returns:
        Response: JSON response with a success message if the user is created successfully,
                  or an error message if the username is already taken or validation fails.

    """
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        # Perform basic validation
        if not username or not password:
            return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Check if the username already exists
            user = User.objects.get(username=username)
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            # Create a new user
            user = User.objects.create_user(username=username, password=password)
            return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
def edit_user(request, username):
    """
    Edit user details using PUT or PATCH method.

    Retrieves the user with the given username from the database. If the user exists,
    the view checks the request method. If the method is PUT, the view updates the user's
    details (username and password) using the provided data. If the method is PATCH, the view
    updates the user's details based on the provided data (either username or password).

    For PUT method:
    - New username and password are required.
    - The new username must be unique (not taken by other users).
    - The user's details are updated in the database.

    For PATCH method:
    - Either username or password can be updated.
    - The new username must be unique (not taken by other users).
    - The user's details are updated in the database.

    If the user does not exist, a 404 Not Found response is returned.

    Parameters:
        request (HttpRequest): The HTTP request object.

        username (str): The username of the user to edit.

    Returns:
        Response: JSON response with a success message on successful update (PUT/PATCH),
                  or an error message if the user is not found or validation fails.

    """
    try:
        # Check if the user exists
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        # Update user details using PUT data
        new_username = request.data.get('username')
        new_password = request.data.get('password')

        # Perform basic validation
        if not new_username or not new_password:
            return Response({'error': 'Both username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the new username is already taken
        if new_username != username and User.objects.filter(username=new_username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user.username = new_username
        user.set_password(new_password)
        user.save()
        return Response({'message': 'User updated successfully.'}, status=status.HTTP_200_OK)

    elif request.method == 'PATCH':
        # Update user details using PATCH data
        new_username = request.data.get('username')
        new_password = request.data.get('password')

        # Check if the new username is already taken
        if new_username and new_username != username and User.objects.filter(username=new_username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)

        user.save()
        return Response({'message': 'User updated successfully.'}, status=status.HTTP_200_OK)

def home(request):
    """
    Render the home page.

    Renders the 'home.html' template, which serves as the home page of the website.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered 'home.html' template.
    """
    return render(request, 'home.html')

def signup(request):
    """
    Handle user signup.

    If POST request, validate the signup form data, create a new user account,
    log in the user, and redirect to 'groups' page.

    If GET request, render the 'signup.html' template with the signup form.

    Parameters:
        request (HttpRequest): The HTTP request object containing user form input.

    Returns:
        HttpResponse: Redirect to 'groups' page on successful signup (POST),
                      or render 'signup.html' template with signup form (GET).
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('groups')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def group(request, slug):
    """
    Display a group and its associated messages.

    Retrieves the group with the given slug from the database. Then, fetches all
    messages associated with the group. Finally, renders the 'group.html' template
    with the retrieved group and messages.

    Parameters:
        request (HttpRequest): The HTTP request object.

        slug (str): The slug of the group to display.

    Returns:
        HttpResponse: Rendered 'group.html' template with the group and messages data.

    Raises:
        Http404: If the group with the given slug does not exist.
    """
    group = Group.objects.get(slug=slug)
    messages = Message.objects.filter(group=group)

    return render(request, 'group.html', {'group': group, 'messages': messages})


@login_required
def groups(request):
    """
    Display the groups associated with the logged-in user.

    Retrieves all groups in the database where the logged-in user is a member.
    Then, renders the 'groups.html' template with the retrieved groups and the
    logged-in user.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered 'groups.html' template with the user's groups.
    """
    groups = Group.objects.filter(members=request.user)
    return render(request, 'groups.html', {'groups': groups, 'user': request.user})

@login_required
def create_group(request):
    """
    Handle group creation.

    If POST request, validate the group form data. If the form is valid and the
    group name is unique, create a new group with the provided data. The group's
    slug is generated from the name, and the logged-in user becomes the group's
    admin and a member. Then, redirect to the newly created group's page.

    If GET request, render the 'create_group.html' template with the group creation form.

    Parameters:
        request (HttpRequest): The HTTP request object containing user form input.

    Returns:
        HttpResponse: Redirect to the newly created group's page on successful group creation (POST),
                      or render 'create_group.html' template with the group creation form (GET).
    """
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group_obj = Group.objects.filter(name=group.name)
            if not group_obj:
                slug = group.name
                group.slug = slug.replace(' ','_').lower()
                group.admin = request.user
                group.save()
                group.members.add(request.user)
                return redirect('group', slug=group.slug)
            else:
                messages.warning(request, f'A group name {group.name} already exists...')
    else:
        form = GroupForm()
    return render(request, 'create_group.html', {'form': form})


@login_required
def delete_group(request, slug):
    """
    Handle group deletion or leaving group.

    Retrieves the group with the given slug from the database. If the group exists,
    the view checks the request method. If the request method is POST and the user
    is the group admin, the group is deleted from the database. If the user is not
    the group admin, they are removed from the group's members. Then, redirect to
    the 'groups' page.

    If the group does not exist, redirect to the 'groups' page.

    Parameters:
        request (HttpRequest): The HTTP request object.

        slug (str): The slug of the group to delete or leave.

    Returns:
        HttpResponse: Redirect to 'groups' page after successful deletion or leaving,
                      or redirect to 'groups' page if the group does not exist.
    """
    try:
        group = get_object_or_404(Group, slug=slug)
    except:
        return redirect('groups')
    if request.method == 'POST':
        if group.admin == request.user.username:
            group.delete()
            return redirect('groups')
        else:
            user_name = User.objects.get(username=request.user.username)
            group.members.remove(user_name)
            return redirect('groups')
    return render(request, 'delete_group.html', {'group': group})


@login_required
def add_members(request, slug):
    """
    Handle adding members to a group.

    Retrieves the group with the given slug from the database. If the group exists,
    the view fetches all users from the database. If the request method is POST,
    the view tries to add a member to the group based on the provided member's username.
    If the username corresponds to an existing user, they are added to the group's members.
    If the username does not match any user, the view does nothing. Then, redirect to
    the group's page.

    If the group does not exist, redirect to the 'groups' page.

    Parameters:
        request (HttpRequest): The HTTP request object.

        slug (str): The slug of the group to which members will be added.

    Returns:
        HttpResponse: Redirect to the group's page after successful member addition,
                      or redirect to 'groups' page if the group does not exist.
    """
    try:
        group = get_object_or_404(Group, slug=slug)
    except:
        return redirect('groups')
    all_users = User.objects.all()
    if request.method == 'POST':
        member_username = request.POST.get('member_username')
        try:
            member = User.objects.get(username=member_username)
            group.members.add(member)
        except User.DoesNotExist:
            pass
        return redirect('group', slug=slug)
    return render(request, 'add_members.html', {'group': group, 'all_users': all_users})

@login_required
def group_users(request, slug):
    """
    Retrieve group members' usernames as JSON response.

    Retrieves the group with the given slug from the database. If the group exists,
    the view fetches all users who are members of the group. Then, it creates a JSON
    response containing a list of dictionaries, where each dictionary represents a
    user with their 'username' key. The view returns this JSON response.

    If the group does not exist, redirect to the 'groups' page.

    Parameters:
        request (HttpRequest): The HTTP request object.

        slug (str): The slug of the group for which to retrieve members.

    Returns:
        JsonResponse: JSON response containing the usernames of group members.
    """
    try:
        group = get_object_or_404(Group, slug=slug)
    except:
        return redirect('groups')
    users = group.members.all()
    user_data = [{'username': user.username} for user in users]
    return JsonResponse({'users': user_data})

@login_required
def search_groups(request):
    """
    Display search results for groups.

    Retrieves the 'query' parameter from the request's GET parameters. If the 'query'
    parameter is provided, the view searches for groups in the database whose name
    contains the 'query' as a case-insensitive substring. Then, it renders the
    'search_groups.html' template with the search results.

    If the 'query' parameter is not provided, or no matching groups are found, the view
    renders the template with no results.

    Parameters:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Rendered 'search_groups.html' template with search results
                      or no results.
    """
    query = request.GET.get('query')
    if query:
        groups = Group.objects.filter(name__icontains=query)
    else:
        groups = Group.objects.none()
    return render(request, 'search_groups.html', {'groups': groups, 'query': query})
