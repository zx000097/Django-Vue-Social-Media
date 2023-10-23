<template>
  <div class="max-w-7xl mx-auto grid grid-cols-4 gap-4">
    <div class="main-left col-span-1">
      <div class="p-4 bg-white border border-gray-200 text-center rounded-lg">
        <img src="https://i.pravatar.cc/300?img=70" class="mb-6 rounded-full" />

        <p>
          <strong>{{ this.user.name }}</strong>
        </p>

        <div class="mt-6 flex space-x-8 justify-around">
          <p class="text-xs text-gray-500">{{ user.friends_count }} friends</p>
          <p class="text-xs text-gray-500">120 posts</p>
        </div>
      </div>
    </div>

    <div class="main-center col-span-2 space-y-4">
      <div class="p-4 bg-white border border-gray-200 rounded-lg" v-if="friendshipRequests.length">
        <h2 class="text-xl mb-6">Friendship Requests</h2>
        <div
          class="p-4 text-center bg-gray-100 rounded-lg"
          v-for="request in friendshipRequests"
          v-bind:key="request.id"
        >
          <img src="https://i.pravatar.cc/100?img=70" class="mb-6 mx-auto rounded-full" />

          <p>
            <strong>
              <RouterLink :to="{ name: 'profile', params: { id: request.created_by.id } }">{{
                request.created_by.name
              }}</RouterLink>
            </strong>
          </p>

          <div class="mt-6 flex space-x-8 justify-around">
            <p class="text-xs text-gray-500">{{ request.created_by.friends_count }} friends</p>
            <p class="text-xs text-gray-500">120 posts</p>
          </div>

          <div class="mt-6 space-x-4">
            <button
              @click="handleRequest('accepted', request.created_by.id)"
              class="inline-block py-4 px-6 bg-purple-600 text-white rounded-lg"
            >
              Accept
            </button>
            <button
              @click="handleRequest('rejected', request.created_by.id)"
              class="inline-block py-4 px-6 bg-red-600 text-white rounded-lg"
            >
              Reject
            </button>
          </div>
        </div>
        <hr />
      </div>

      <div
        class="p-4 bg-white border border-gray-200 rounded-lg grid grid-cols-2 gap-4"
        v-if="friends.length"
      >
        <div
          class="p-4 text-center bg-gray-100 rounded-lg"
          v-for="user in friends"
          v-bind:key="user.id"
        >
          <img src="https://i.pravatar.cc/300?img=70" class="mb-6 rounded-full" />

          <p>
            <strong>
              <RouterLink :to="{ name: 'profile', params: { id: user.id } }">{{
                user.name
              }}</RouterLink>
            </strong>
          </p>

          <div class="mt-6 flex space-x-8 justify-around">
            <p class="text-xs text-gray-500">{{ user.friends_count }} friends</p>
            <p class="text-xs text-gray-500">120 posts</p>
          </div>
        </div>
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
import { useToastStore } from '@/stores/toast'

export default {
  name: 'FriendsView',
  components: {
    PeopleYouMayKnow,
    Trends
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
      user: [],
      friendshipRequests: [],
      friends: []
    }
  },
  mounted() {
    this.getFriends()
  },

  methods: {
    getFriends() {
      axios
        .get(`/accounts/friends/${this.$route.params.id}`)
        .then((response) => {
          this.friendshipRequests = response.data.requests
          this.friends = response.data.friends
          this.user = response.data.user
          console.log(response.data)
        })
        .catch((error) => {
          console.log(error)
        })
    },

    handleRequest(status, createdById) {
      console.log(status)
      axios
        .post(`/accounts/friends/${createdById}/${status}`)
        .then((response) => {})
        .catch((error) => {})
    }
  }
}
</script>
