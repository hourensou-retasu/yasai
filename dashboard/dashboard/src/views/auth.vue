<template>
  <span>認証用リダイレクトページ</span>
</template>

<script>
import axios from 'axios'

export default {
  name: 'auth',
  async mounted() {
    if(!this.$route.query.code) {
      this.$router.push('dashboard')
      return
    }

    const authCode = this.$route.query.code
    const url = `http://localhost:8000/token?code=${ authCode }`
    const res = await axios.get(url)

    console.log(res)

    localStorage.setItem('accessToken', res.data.access_token)
    localStorage.setItem('refreshToken', res.data.refresh_token)

    this.$router.push('dashboard')

  }
}
</script>