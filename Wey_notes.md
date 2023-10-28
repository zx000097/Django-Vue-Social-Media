# Wey Notes

## Customizing authentication

#### Background

From [Customizing authentication in Django | Django documentation | Django](https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project), it is highly recommended to set up a custom user model. We can either extend the AbstractUser which keeps the default User fields and permissions, or extend AbstractBaseUser.

There are four steps for adding a custom user model:

1. Create a CustomUser model

2. Update settings.py

3. Customize UserCreationForm and UserChangeForm

4. Add the custom user model to admin.py

We wil also need a Custom User Manager. From [Managers | Django documentation | Django](https://docs.djangoproject.com/en/4.2/topics/db/managers/) , a Manager is the interface through which database query operations are provided to Django models. For example, we get a QuerySet by using our model's Manager. Each model has at least one Manager, and it's called objects by default

```python
Blog.objects
```

#### Implementation

Referencing https://testdriven.io/blog/django-custom-user-model/ https://testdriven.io/blog/django-custom-user-model

First, we start by doing a TDD approach. We create a UserManagerTest, that tests our custom manager to create a normal user and a super user.

```python
def test_create_user(self):
    User = get_user_model()
    user = User.objects.create_user(email="normal@user.com", name="normal", password="foo")
    self.assertEqual(user.email, "normal@user.com")
    self.assertEqual(user.name, "normal")
    self.assertTrue(user.is_active)
    self.assertFalse(user.is_staff)
    self.assertFalse(user.is_superuser)

    with self.assertRaises(TypeError):
        User.objects.create_user()
    with self.assertRaises(TypeError):
        User.objects.create_user(email="")
    with self.assertRaises(ValueError):
        User.objects.create_user(email="", password="foo")
```

In the above test, we create a user using the Manager (User.objects), and then test the attributes. We should raise exception when email is empty, because that is the main thing we use to identify different users. The super user test follows the similar fashion, except the is_staff and is_superuser are expected to be true.

Next, we start to implement the Manager. 

```python
class CustomUserManager(BaseUserManager):
    def _create_user(self, name, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided a valid e-mail address!")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(name, email, password, **extra_fields)

    def create_superuser(self, name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(name, email, password, **extra_fields)
```

We create a private module function, with a single leading underscore. It will raise an exception if the email is not passed in. We then use the private function in our create_user and create_superuser method. From [Python Dictionary setdefault() Method](https://www.w3schools.com/python/ref_dictionary_setdefault.asp)[Python Dictionary setdefault() Method](https://www.w3schools.com/python/ref_dictionary_setdefault.asp), the setdefault() is inserting the key and value into the extra_fields if the kvp does not exist.

The next thing is our User. 

```python
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, default="")
    avatar = models.ImageField(upload_to="avatars", blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []
```

From the above, we added a bunch fields that we are interested in. By setting the objects to our manager, we specified that all objects for the class will come from the CustomUserManager. 

The capital letter fields at the end, are from [Customizing authentication in Django | Django documentation | Django](https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#django.contrib.auth.models.CustomUser). 

- The USERNAME_FIELD defines the unique identifier for our User model, and in our case it is the email address. 

- The REQUIRED_FIELDS is a list of the field names that will be prompted for when creating a user via the createsuperuser command. 

We don't need to test models as long as it does not have any extra logic, as per [GitHub - HackSoftware/Django-Styleguide: Django styleguide used in HackSoft projects](https://github.com/HackSoftware/Django-Styleguide#testing)

The next thing is to update the AUTH_USER_MODEL in the settings to be our custom user.

```python
AUTH_USER_MODEL = "accounts.User"
```

Now, after the migration, if I use the createsuperuser command, it should prompt for email instead of username. 

## SignUp API

#### Implementation

Create a SignupForm that inherits from the UserCreationForm, which is new in Django [Using the Django authentication system | Django documentation | Django](https://docs.djangoproject.com/en/4.2/topics/auth/default/#django.contrib.auth.forms.BaseUserCreationForm).

- It has 3 fields: username, password1 and password2. 

- It verfies that password1 and password2 match.

- We use UserCreationForm that checks for repeated usernames. Same usernames but different cases are not allowed.

```python
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "name", "password1", "password2")
```

Create a SignUpView that inherits the GenericAPIView. Because we are sending data when signing up, we define the post method. The post method uses the form above.

```python
class SignUpView(APIView):
    def post(self, request):
        data = request.data

        form = SignupForm(
            {
                "email": data.get("email"),
                "name": data.get("name"),
                "password1": data.get("password1"),
                "password2": data.get("password2"),
            }
        )

        if form.is_valid():
            form.save()
        else:
            return Response(
                {"errors": f"{get_dict_values_string(form.errors)}!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"status": "Successfully created user."}, status=status.HTTP_201_CREATED
        )
```

The form could fail because of multiple users with the same email, same name etc. The error is a Python dictionary,  [Django: All Form Error Messages as a single string - Stack Overflow](https://stackoverflow.com/questions/38961387/django-all-form-error-messages-as-a-single-string) shows how to get a string out from django from errors. I have defined the function in a utils class.

#### Testing

Added a test that tests if we can use the endpoint to create a user.

```python
class SignUpViewTest(APITestCase):
    def test_create_user(self):
        url = reverse("signup")
        data = {
            "name": "hoho",
            "email": "hoho@gmail.com",
            "password1": "qpalzm102938",
            "password2": "qpalzm102938",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, "hoho")
        self.assertEqual(User.objects.get().email, "hoho@gmail.com")
```

I am not testing password as apparently the django form will hash the password. 

## Login

Basically, two types of tokens are playing a big role here: access token and refresh token. [How to Use JWT Authentication with Django REST Framework](https://simpleisbetterthancomplex.com/tutorial/2018/12/19/how-to-use-jwt-authentication-with-django-rest-framework.html)

- The access token is the one that provides access to the protected resource, with a short lifespan. 

- When the access token is expired, we could use the refresh token to get a new access token from the server.

For Login, we are using the JWT's TokenObtainPairView. It checks the email and password posted from the frontend, and then returns a pair of tokens (refresh and access) if they are valid. The frontend will store the tokens, and then use the access token to set the authorization header.

```javascript
await axios
          .post('/api/login/', this.form)
          .then((response) => {
            console.log(response.data)
            this.userStore.setToken(response.data)

            axios.defaults.headers.common['Authorization'] = 'Bearer ' + response.data.access
          })
          .catch((error) => {
            console.log('error', error)
          })
```

With this setup, the requests that we send afterwards will include the token in it. The backend Django will thus know we are authenticated (logged in). We have setup the DRF authentication settings like so:

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}
```

This settings will be applied to all the views we have. For the signup view, we should not need to be authenticated or permission. Override the settings in the class: [Setting the authentication scheme](https://www.django-rest-framework.org/api-guide/authentication/#setting-the-authentication-scheme)

```python
authentication_classes = []
permission_classes = []
```

After login, we want to use the token to access the user information. We create an endpoint for this:

```python
class MeView(APIView):
    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "name": request.user.name,
                "email": request.user.email ,
            }
        )
```

Django somehow figures out all the information with the access token in our request header. 

## Post

Created two models: Post and Attachment. They inherit from a base class that has id and created_at fields.

```python
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Attachment(BaseModel):
    image = models.ImageField(upload_to="attachments/")
    created_by = models.ForeignKey(
        User, related_name="post_attachments", on_delete=models.CASCADE
    )


class Post(BaseModel):
    body = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    attachments = models.ManyToManyField(Attachment, blank=True)
```

From above, the post and attachment have a many to many relationships. I guess it is because a post can have multiple attachments, and an attachment could be used in multiple posts.

The related_name field in a ForeignKey let us refer to the other object easier, i.e. to get all the posts from a user, we could just user.posts, instead of the default user.post_set by Django, https://stackoverflow.com/questions/2642613/what-is-related-name-used-for 

 Next bit is creating a PostSerializer:

```python
class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField("format_created_at")

    def format_created_at(self, post):
        return timesince(post.created_at)
    class Meta:
        model = Post
        fields = ("id", "created_by", "body", "created_at")
```

Notice here we are using another Serializer to serialize the created_by field, as it is a Foreign key and we need its own serializer to serialize it. We are also using a django utility timesince function to get the formatted time for the serializer and thus frontend can display the time at a more readable way.

#### All Posts Endpoint

Create a endpoint for retreving all the posts.

```python
class PostListView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
```

Some test:

```python
class PostListViewTests(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )
        self.user2 = get_user_model().objects.create_user(
            name="another testuser", email="anothertestuser@gmail.com", password="test"
        )
        Post.objects.get_or_create(body="Something", created_by=self.user1)
        Post.objects.get_or_create(body="Something2", created_by=self.user1)
        Post.objects.get_or_create(body="Something", created_by=self.user2)
        user1_refresh_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user1_refresh_token.access_token}"
        )

    def test_get_all_posts(self):
        url = reverse("posts")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 3)
```

#### Create Post Endpoint

```python
class PostCreateView(APIView):
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(created_by=request.user)
            post.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
```

Only save the post to the database if it is valid. The created_by=request.user inside the serializer.save() is saying save this instance with this property set to that.

Some tests:

```python
class PostCreateViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )

        user_refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_refresh_token.access_token}"
        )

    def test_create_post(self):
        url = reverse("create_post")
        response = self.client.post(url, {"created_by": self.user, "body": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["body"], "Hello")
        self.assertEqual(response.data["created_by"]["id"], str(self.user.id))

    def test_create_post_fail_without_token(self):
        self.client.credentials()
        url = reverse("create_post")
        response = self.client.post(url, {"created_by": self.user, "body": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_fail_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer randomtoken12345")
        url = reverse("create_post")
        response = self.client.post(url, {"created_by": self.user, "body": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

Doing client.credentials() will clear the request token.

#### Profile Posts Endpoint

```python
class ProfilePostListView(APIView):
    def get(self, request):
        posts = Post.objects.filter(created_by_id=request.user.id)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
```

Here we want to filter all the posts with just the id coming from the request. The request sent from the frontend will contain the access token, and the middle ware will figure out the corresponding user. Then as mentioned in [Making queries | Django documentation | Django](https://docs.djangoproject.com/en/4.2/topics/db/queries/#field-lookups), we can fitler with the foreign key id with "_id".

We can create a test for this:

```python
class ProfilePostListViewTests(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )
        self.user2 = get_user_model().objects.create_user(
            name="another testuser", email="anothertestuser@gmail.com", password="test"
        )
        Post.objects.get_or_create(body="Something", created_by=self.user1)
        Post.objects.get_or_create(body="Something2", created_by=self.user1)
        Post.objects.get_or_create(body="Something", created_by=self.user2)
        user1_refresh_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user1_refresh_token.access_token}"
        )

   def test_posts_only_from_given_id(self):
        url = reverse("profile_posts", kwargs={"id": self.user2.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data["posts"]), 2)
        for post in response.data["posts"]:
            self.assertEquals(post["created_by"]["id"], str(self.user2.id))
        self.assertEqual(response.data["user"]["id"], str(self.user2.id))

    def test_empty_post_still_return_profile_username(self):
        another_user = get_user_model().objects.create_user(
            name="anotherrrr testuser",
            email="anotherrrtestuser@gmail.com",
            password="test",
        )
        url = reverse("profile_posts", kwargs={"id": another_user.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data["posts"]), 0)
        self.assertEqual(response.data["user"]["id"], str(another_user.id))
```

- Creating 3 posts, 2posts are from the user1 and another is from the user 2</p>

- Get the refresh token for the user1 and set the client header to include the token as mentioned in https://stackoverflow.com/a/62787814 and [Testing - Django REST framework](https://www.django-rest-framework.org/api-guide/testing/#credentialskwargs) 

First test simply checks if all the posts user id belong to provided id: user2 id. Response.data is a list of OrderedDict, and the post['created_by'] is another OrderedDict for the User model. Note that this request is sent by user1 with its access token.

Next test ensures we still return profile username when there are no posts.

## Search

Because search does not really belong to the accounts and posts app, we create its own app. 

#### Search Endpoint

```python
class SearchView(APIView):
    def post(self, request):
        users = User.objects.filter(name__icontains=request.data["query"])
        users_seralizer = UserSerializer(users, many=True)

        return Response(users_seralizer.data, status=status.HTTP_200_OK)
```

The front end will set its query string into the query tag. We extract that, find all the related users, and use serializer to seralize before returning them. Of course, we have a test:

```python
class SearchViewTest(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create(
            name="user1", email="user1@gmail.com", password="test"
        )
        self.user2 = get_user_model().objects.create(
            name="user2", email="user2@gmail.com", password="test"
        )
        self.abc_user = get_user_model().objects.create(
            name="abc", email="abc@gmail.com", password="test"
        )
        user1_refresh_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user1_refresh_token.access_token}"
        )
        Post.objects.create(body="i contains a user", created_by=self.abc_user)
        Post.objects.create(body="not in query!", created_by=self.user1)

    def test_search_return_query_result(self):
        url = reverse("search")
        response = self.client.post(url, {"query": "user"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["users"]), 2)
        self.assertTrue(all("user" in user["name"] for user in response.data["users"]))

        self.assertEqual(len(response.data["posts"]), 1)
        self.assertTrue("user" in response.data["posts"][0]["body"])
```

The test checks if the returned result only contains the users with the name similar to "user". The response data is a list of users, each of them is an ordered dictionary. Use the all keyword to check if all of them [python - How to check if all elements of a list match a condition? - Stack Overflow](https://stackoverflow.com/questions/10666163/how-to-check-if-all-elements-of-a-list-match-a-condition) has the substring "user" in the names [Does Python have a string &#39;contains&#39; substring method? - Stack Overflow](https://stackoverflow.com/questions/3437059/does-python-have-a-string-contains-substring-method). 

We also check the same thing in the returned posts - checking the body.

## Friendship

```python
class FriendshipRequest(models.Model):
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

    STATUS_CHOICES = ((SENT, "Sent"), (ACCEPTED, "Accepted"), (REJECTED, "Rejected"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, related_name="created_friendship_requests", on_delete=models.CASCADE
    )
    created_for = models.ForeignKey(
        User, related_name="received_friendship_requests", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SENT)
```

Added a new model for the request. It has created_by and created_for fields, which indicates who is sending and receiving the request. It also has a status enum, marking if the request is sent, accepted or rejected.

#### Add Friend Endpoint

```python
class AddFriendView(APIView):
    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        FriendshipRequest.objects.create(
            created_for=user, created_by=request.user
        )
        return Response(
            {"message": "friendship request created"},
            status=status.HTTP_201_CREATED,
        )

class AddFriendViewTest(APITestCase):
    def setUp(self):
        self.to_be_added = User.objects.create_user(
            email="friend@abc.com", name="friend", password="foo"
        )
        self.myself = User.objects.create_user(
            email="myself@abc.com", name="myself", password="foo"
        )
        user_refresh_token = RefreshToken.for_user(self.myself)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_refresh_token.access_token}"
        )

    def test_add_friend(self):
        url = reverse("add_friend", kwargs={"id": self.to_be_added.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendshipRequest.objects.count(), 1)
        self.assertEqual(FriendshipRequest.objects.get().created_by.id, self.myself.id)
        self.assertEqual(
            FriendshipRequest.objects.get().created_for.id, self.to_be_added.id
        )
        self.assertEqual(self.myself.created_friendship_requests.count(), 1)
        self.assertEqual(self.myself.received_friendship_requests.count(), 0)
        self.assertEqual(self.to_be_added.created_friendship_requests.count(), 0)
        self.assertEqual(self.to_be_added.received_friendship_requests.count(), 1)

    def test_add_invalid_user(self):
        url = reverse("add_friend", kwargs={"id": str(uuid.uuid4())})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(FriendshipRequest.objects.count(), 0)
        self.assertEqual(self.myself.created_friendship_requests.count(), 0)
        self.assertEqual(self.myself.received_friendship_requests.count(), 0)
```

This endpoint is handling post request from the frontend, creating a new friendship in the database. 

#### View Friends Endpoint

This endpoint returns a list of current friends. If the current logged in user is viewing its own friend page, this endpoint also returns a list of friendship requests.

```python
class GetFriendsView(APIView):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        requests = []
        if user == request.user:
            requests = FriendshipRequest.objects.filter(created_for=request.user)
        friends = user.friends.all()
        return Response(
            {
                "user": UserSerializer(user).data,
                "friends": UserSerializer(friends, many=True).data,
                "requests": FrienshipRequestSerializer(requests, many=True).data,
            },
            status=status.HTTP_200_OK,
        )

```

#### Testing

```python
class GetFriendsViewTest(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="friend@abc.com", name="friend", password="foo"
        )
        self.user_b = User.objects.create_user(
            email="myself@abc.com", name="myself", password="foo"
        )
        self.user_c = User.objects.create_user(
            email="ccc@abc.com", name="ccc", password="foo"
        )
        FriendshipRequest.objects.create(
            created_for=self.user_c, created_by=self.user_a
        )
        self.user_a.friends.add(self.user_b)
        user_b_refresh_token = RefreshToken.for_user(self.user_b)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_b_refresh_token.access_token}"
        )

    def test_get_a_friend_view(self):
        url = reverse("friends", kwargs={"id": self.user_a.id})
        response = self.client.get(url)
        user = response.data["user"]
        friends = response.data["friends"]
        requests = response.data["requests"]

        self.assertEqual(user["id"], str(self.user_a.id))
        self.assertEqual(len(friends), 1)
        self.assertEqual(friends[0]["id"], str(self.user_b.id))
        self.assertEqual(len(requests), 0)

    def test_get_b_friend_view(self):
        url = reverse("friends", kwargs={"id": self.user_b.id})
        response = self.client.get(url)
        user = response.data["user"]
        friends = response.data["friends"]
        requests = response.data["requests"]

        self.assertEqual(user["id"], str(self.user_b.id))
        self.assertEqual(len(friends), 1)
        self.assertEqual(friends[0]["id"], str(self.user_a.id))
        self.assertEqual(len(requests), 0)

        def test_get_c_friend_view(self):
        url = reverse("friends", kwargs={"id": self.user_c.id})
        response = self.client.get(url)
        user = response.data["user"]
        friends = response.data["friends"]
        requests = response.data["requests"]

        self.assertEqual(user["id"], str(self.user_c.id))
        self.assertEqual(len(friends), 0)
        self.assertEqual(len(requests), 0)

    def test_others_viewing_c_friendpage_will_not_show_requests(self):
        FriendshipRequest.objects.create(
            created_for=self.user_c, created_by=self.user_a
        )
        url = reverse("friends", kwargs={"id": self.user_c.id})
        response = self.client.get(url)
        requests = response.data["requests"]

        self.assertEqual(len(requests), 0)

    def test_c_viewing_c_friendpage_will_show_requests(self):
        FriendshipRequest.objects.create(
            created_for=self.user_c, created_by=self.user_a
        )
        user_refresh_token = RefreshToken.for_user(self.user_c)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_refresh_token.access_token}"
        )
        url = reverse("friends", kwargs={"id": self.user_c.id})
        response = self.client.get(url)
        requests = response.data["requests"]
        self.assertEqual(len(requests), 1)
        self.assertTrue(requests[0]["created_for"]["id"], str(self.user_c.id))
        self.assertTrue(requests[0]["created_by"]["id"], str(self.user_a.id))
```

In the setup, we have user a, b and c. User a and b are friends. We log in as user b. The tests are:

- Viewing a's friend page, should show b as the only friend, and no request.

- Viewing b's friend page, should show a as the only friend, and no request.

- Viewing c's friend page, should show no friend, no request.

- Send a request to c, and view c's friend page. Should show 0 request as we are not logged in as c.

- Send a request to c, log in as c, and view c's friend page. Should show 1 request.



## Likes

The Like model will have a many-to-one relationship with Post, so we will use Foreign Key here.

```python
class Like(BaseModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
```

#### Endpoint

A post endpoint - like the post, or unlike if the post has already been already liked.

```python
class LikePostView(APIView):
    def post(self, request, id):
        post = get_object_or_404(Post, id=id)

        try:
            like = Like.objects.get(created_by=request.user, post=post)
        except Like.DoesNotExist:
            like = Like.objects.create(created_by=request.user, post=post)
            like.save()

            return Response(
                {
                    "likes": str(post.like_set.count()),
                    "message": "Successfully Liked.",
                },
                status=status.HTTP_200_OK,
            )

        like.delete()
        return Response(
            {"likes": str(post.like_set.count()), "message": "Successfully Unliked."},
            status=status.HTTP_200_OK,
        )

```

#### Testing

```python
class LikePostViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )

        self.post = Post.objects.create(body="Something", created_by=self.user)
        user_refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_refresh_token.access_token}"
        )

    def test_like_post(self):
        url = reverse("like_post", kwargs={"id": str(self.post.id)})
        response = self.client.post(url)
        self.assertEqual(response.data["likes"], str(1))
        self.assertEqual(self.post.like_set.count(), 1)
        self.assertEqual(Like.objects.count(), 1)

    def test_like_already_liked_post_will_unlike(self):
        Like.objects.create(post=self.post, created_by=self.user)
        url = reverse("like_post", kwargs={"id": str(self.post.id)})
        response = self.client.post(url)
        self.assertEqual(response.data["likes"], str(0))
        self.assertEqual(self.post.like_set.count(), 0)
        self.assertEqual(Like.objects.count(), 0)
```
