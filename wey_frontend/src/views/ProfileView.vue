<template>
  <div class="max-w-7xl mx-auto grid grid-cols-4 gap-4">
    <div class="main-left col-span-1">
      <div class="p-4 bg-white border border-gray-200 text-center rounded-lg">
        <img src="https://i.pravatar.cc/300?img=70" class="mb-6 rounded-full" />

        <p>
          <strong>{{ this.user.name }}</strong>
        </p>

        <div class="mt-6 flex space-x-8 justify-around">
          <RouterLink
            :to="{ name: 'friends', params: { id: user.id } }"
            class="text-xs text-gray-500"
            >{{ user.friends_count }} friends</RouterLink
          >
          <p class="text-xs text-gray-500">120 posts</p>
        </div>

        <div class="mt-6">
          <button
            v-if="userStore.user.id !== user.id"
            class="inline-block py-4 px-6 bg-purple-600 text-white rounded-lg"
            @click="sendFriendRequest"
          >
            Add Friend
          </button>
          <button
            v-else
            class="inline-block py-4 px-6 bg-red-600 text-white rounded-lg"
            @click="logout"
          >
            Log out
          </button>
        </div>
      </div>
    </div>

    <div class="main-center col-span-2 space-y-4">
      <div class="bg-white border border-gray-200 rounded-lg" v-if="userStore.user.id === user.id">
        <form v-on:submit.prevent="submitForm" method="post">
          <div class="p-4">
            <textarea
              v-model="body"
              class="p-4 w-full bg-gray-100 rounded-lg"
              placeholder="What are you up to?"
            ></textarea>
          </div>

          <div class="p-4 border-t border-gray-100 flex justify-between">
            <a href="#" class="inline-block py-4 px-6 bg-gray-600 text-white rounded-lg"
              >Attach Image</a
            >
            <button class="inline-block py-4 px-6 bg-purple-600 text-white rounded-lg">Post</button>
          </div>
        </form>
      </div>

      <div
        class="p-4 bg-white border border-gray-200 rounded-lg"
        v-for="post in posts"
        v-bind:key="post.id"
      >
        <FeedItem v-bind:post="post" />
      </div>
    </div>

    <div class="main-right col-span-1 space-y-4">
      <PeopleYouMayKnow />

      <Trends />
    </div>
  </div>
</template>

<script>
import PeopleYouMayKnow from '../components/PeopleYouMayKnow.vue'
import Trends from '../components/Trends.vue'
import axios from 'axios'
import { useUserStore } from '@/stores/user'
import FeedItem from '../components/FeedItem.vue'
import { RouterLink } from 'vue-router'
import { useToastStore } from '@/stores/toast'

export default {
  name: 'ProfileView',
  components: {
    PeopleYouMayKnow,
    Trends,
    FeedItem,
    RouterLink
  },
  setup() {
    const userStore = useUserStore()
    const toastStore = useToastStore()
    return {
      userStore,
      toastStore
    }
  },
  data() {
    return {
      posts: [],
      body: [],
      user: []
    }
  },
  mounted() {
    this.getFeed()
  },
  watch: {
    '$route.params.id': {
      handler: function () {
        this.getFeed()
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    sendFriendRequest() {
      axios
        .post(`/accounts/friends/${this.$route.params.id}/request`)
        .then((response) => {
          this.toastStore.showToast(5000, 'The request is sent successfully.', 'bg-emerald-300')
        })
        .catch((error) => {
          this.toastStore.showToast(5000, 'The request has already been sent!', 'bg-red-300')
        })
    },
    getFeed() {
      axios
        .get(`posts/profile/${this.$route.params.id}`)
        .then((response) => {
          this.posts = response.data.posts
          this.user = response.data.user
          console.log(this.user.id)
        })
        .catch((error) => {
          console.log(error)
        })
    },
    submitForm() {
      axios
        .post('posts/create', { body: this.body })
        .then((response) => {
          this.body = ''
          this.posts.unshift(response.data)
        })
        .catch((error) => {
          console.log(error)
        })
    },
    logout() {
      this.userStore.removeToken()
      this.$router.push('/login')
    }
  }
}
</script>
