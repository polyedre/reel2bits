<template>
  <div class="row mt-4">
    <div class="col-md-8">
      <Announcement />
      <TimelineTabs active="public" />

      <Timeline
        timeline-name="public"
      />
    </div>
    <div class="col-md-4">
      <!--<Sidebar />-->
    </div>
  </div>
</template>

<script>
import TimelineTabs from '../timeline_tabs/timeline_tabs.vue'
import Timeline from '../timeline/timeline.vue'
import Sidebar from '../sidebar/sidebar.vue'
import Announcement from '../announcement/announcement.vue'

const PublicTimeline = {
  components: {
    TimelineTabs,
    Timeline,
    Sidebar,
    Announcement
  }
}

export default PublicTimeline
</script>
