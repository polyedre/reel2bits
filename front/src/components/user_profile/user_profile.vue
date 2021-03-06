<template>
  <div>
    <div v-if="error">
      {{ error }}
    </div>
    <div v-if="user">
      <div class="row mt-4">
        <div class="col-md-8">
          <b-nav>
            <b-nav-item :active="isTimelineTracks" :to="linkToProfileSpecific(user, 'user-profile-tracks')"
                        class="border-right pr-3"
            >
              <translate translate-context="Content/UserProfile/Tab/Text">
                Tracks
              </translate>
            </b-nav-item>
            <b-nav-item v-if="!isExternal" :active="isTimelineAlbums" :to="linkToProfileSpecific(user, 'user-profile-albums')"
                        class="border-right px-3"
            >
              <translate translate-context="Content/UserProfile/Tab/Text">
                Albums
              </translate>
            </b-nav-item>
            <b-nav-item v-if="isUs" :active="isTimelineDrafts" :to="linkToProfileSpecific(user, 'user-profile-drafts')"
                        class="border-right px-3"
            >
              <translate translate-context="Content/UserProfile/Tab/Text">
                Drafts
              </translate>
            </b-nav-item>
            <b-nav-item v-if="isUs" :active="isTimelineUnprocessed" :to="linkToProfileSpecific(user, 'user-profile-unprocessed')"
                        class="px-3"
            >
              <translate translate-context="Content/UserProfile/Tab/Text">
                Unprocessed
              </translate>
            </b-nav-item>
          </b-nav>

          <Timeline v-if="isTimelineTracks"
                    key="{{ userId }}user"
                    timeline-name="user"
                    :user-id="userId"
          />
          <Timeline v-else-if="isTimelineAlbums"
                    key="{{ userId }}albums"
                    timeline-name="albums"
                    :user-id="userId"
          />
          <Timeline v-else-if="isTimelineDrafts"
                    key="{{ userId }}drafts"
                    timeline-name="drafts"
                    :user-id="userId"
          />
          <Timeline v-else-if="isTimelineUnprocessed"
                    key="{{ userId }}unprocessed"
                    timeline-name="unprocessed"
                    :user-id="userId"
          />
        </div>
        <div class="col-md-4">
          <Sidebar :user="user" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import get from 'lodash/get'
import Timeline from '../timeline/timeline.vue'
import Sidebar from '../sidebar/sidebar.vue'
import fileSizeFormatService from '../../services/file_size_format/file_size_format.js'
import generateRemoteLink from 'src/services/remote_user_link_generator/remote_user_link_generator.js'

export default {
  components: {
    Timeline,
    Sidebar
  },
  data () {
    return {
      error: false,
      userId: null
    }
  },
  computed: {
    user () {
      return this.$store.getters.findUser(this.userId)
    },
    isExternal () {
      return this.$route.name.startsWith('external-user-profile')
    },
    isUs () {
      return this.userId && this.$store.state.users.currentUser.flakeId &&
        this.userId === this.$store.state.users.currentUser.flakeId
    },
    isTimelineTracks () {
      // Can be external- too, uses endsWith to match it
      return this.$route.name.endsWith('user-profile-tracks') || this.$route.name.endsWith('user-profile')
    },
    isTimelineAlbums () {
      return this.$route.name === 'user-profile-albums'
    },
    isTimelineDrafts () {
      return this.$route.name === 'user-profile-drafts'
    },
    isTimelineUnprocessed () {
      return this.$route.name === 'user-profile-unprocessed'
    },
    humanQuota () {
      let quotaCount = ''
      let quotaLimit = ''

      if (this.user.reel2bits.quota_count === 0) {
        quotaCount = '0'
      } else {
        const ffs = fileSizeFormatService.fileSizeFormat(this.user.reel2bits.quota_count)
        quotaCount = ffs.num + ffs.unit
      }

      if (this.user.reel2bits.quota_limit === 0) {
        quotaLimit = '0'
      } else {
        const ffs = fileSizeFormatService.fileSizeFormat(this.user.reel2bits.quota_limit)
        quotaLimit = ffs.num + ffs.unit
      }

      return quotaCount + '/' + quotaLimit
    }
  },
  watch: {
    '$route.params.id': function (newVal) {
      if (newVal) {
        this.cleanUp()
        this.load(newVal)
      }
    },
    '$route.params.name': function (newVal) {
      if (newVal) {
        this.cleanUp()
        this.load(newVal)
      }
    }
  },
  created () {
    const routeParams = this.$route.params
    this.load(routeParams.name || routeParams.id)
  },
  destroyed () {
    this.cleanUp()
  },
  methods: {
    linkToProfileSpecific (user, suffix) {
      return generateRemoteLink(
        user.flakeId, user.screen_name,
        this.$store.state.instance.restrictedNicknames,
        suffix
      )
    },
    load (userNameOrId) {
      console.debug('loading profile for ' + userNameOrId)
      const user = this.$store.getters.findUser(userNameOrId)
      if (user) {
        this.userId = user.flakeId
        console.warn('we already know the user')
      } else {
        this.$store.dispatch('fetchUser', userNameOrId)
          .then(({ flakeId }) => {
            this.userId = flakeId
            console.warn('fetched by ID: ' + flakeId)
          })
          .catch((reason) => {
            console.warn('cannot fetch user: ' + reason)
            const errorMessage = get(reason, 'error.error')
            if (errorMessage) {
              this.error = errorMessage
            } else {
              const msg = this.$pgettext('Content/UserProfile/Error', 'Error loading user: %{errorMsg}')
              this.error = this.$gettextInterpolate(msg, { errorMsg: errorMessage })
            }
            this.$bvToast.toast(this.$pgettext('Content/UserProfile/Toast/Error/Message', 'Cannot fetch user'), {
              title: this.$pgettext('Content/UserProfile/Toast/Error/Title', 'User Profile'),
              autoHideDelay: 5000,
              appendToast: false,
              variant: 'danger'
            })
          })
      }
    },
    cleanUp () {
      // do nothing for now
    }
  }
}
</script>
