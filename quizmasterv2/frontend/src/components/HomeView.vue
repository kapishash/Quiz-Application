<template>
  <div class="d-flex justify-content-center align-items-center vh-100">
    <div class="card-body text-center">
      <h5 class="card-title">Welcome to Quiz Menia</h5>
      <br />
      <p class="card-text">
        The one stop preperation site for all your quizzing and examination needs
      </p>
      <br /><br /><br />
      <router-link to="/admin-login" class="btn btn-primary">Admin Login </router-link>
      &nbsp; &nbsp;
      <router-link to="/student-login" class="btn btn-primary">Student Login </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeView",
};
</script>
