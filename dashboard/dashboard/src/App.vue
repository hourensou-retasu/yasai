<template>
  <div id="app">
    <nav
      class="navbar"
      role="navigation"
      aria-label="main navigation"
    >
      <div class="navbar-brand">
        <router-link
          class="navbar-item"
          to="home"
        >
          <span>Yasai</span>
        </router-link>
      </div>

      <div
        id="navbarBasicExample"
        class="navbar-menu"
      >
        <div class="navbar-start">
          <router-link
            to="dashboard"
            class="navbar-item"
          >
            Dashboard
          </router-link>
        </div>

        <div class="navbar-end">
          <div class="navbar-item">
            <div class="buttons">
              <a
                v-show="isLoggedIn"
                class="button is-light"
                href="https://accounts.secure.freee.co.jp/public_api/authorize?client_id=6e4d11db5993f17638e620aae1f25a38c5c95dcdb0c825d1432994ab1d2b0fc0&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fauth&response_type=code"
              >Log in</a>
            </div>
          </div>
        </div>
      </div>
    </nav>
    <router-view />
  </div>
</template>

<style lang="scss">
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
  a {
    font-weight: bold;
    color: #2c3e50;
    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>

<script>
import "bulma/css/bulma.css";
import "@fortawesome/fontawesome-free/js/all.js";

export default {
  computed: {
    isLoggedIn() {
      return !localStorage.getItem('accessToken')
    }
  }
};
</script>
