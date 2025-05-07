<template>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/admin-dashboard">Quiz Menia</router-link>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/users">Users</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin-subjects">Subjects</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/chapters">Chapters</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/quizzes">Quizzes</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/questions">Questions</router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link" aria-current="page" href="#" @click="logout" style="cursor: pointer;"> Logout </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  methods: {
    logout() {
      localStorage.removeItem("admintoken");
      this.$router.push("/");
      
    },
  },
  name: "NavBar",
};
</script>