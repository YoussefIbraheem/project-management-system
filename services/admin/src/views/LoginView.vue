<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { setTokens } from '../auth'
import { jwtDecode } from 'jwt-decode'

const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  console.log(`USER:${email},${password}`)
  try {
    const response = await axios.post(`${import.meta.env.VITE_AUTH_API_URL}/api/v1/login/`, {
      email: email.value,
      password: password.value,
    })
    const decodedTokens = jwtDecode(response.data.tokens.refresh)
    const isSuperuser = decodedTokens.is_superuser
    console.log(isSuperuser)
    if(!isSuperuser){
      throw new Error("Unauthorized Access");
    }
    console.log(decodedTokens)
    setTokens(response.data.tokens)
    router.push('/projects')
  } catch (err) {
    error.value =
      err.response?.data?.non_field_errors?.[0] ||
      err.response?.data?.detail ||
      'Invalid email or password.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="login-view">
    <form class="login-form" @submit.prevent="handleLogin">
      <h1>Sign in</h1>
      <p v-if="error" class="login-form__error">{{ error }}</p>

      <label class="login-form__field">
        <span>Email</span>
        <input v-model="email" type="email" autocomplete="email" required />
      </label>

      <label class="login-form__field">
        <span>Password</span>
        <input v-model="password" type="password" autocomplete="current-password" required />
      </label>

      <button type="submit" class="login-form__submit" :disabled="loading">
        {{ loading ? 'Signing in...' : 'Sign in' }}
      </button>
    </form>
  </section>
</template>

<style scoped>
.login-view {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

.login-form {
  width: 100%;
  max-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 2rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-background-soft);
}

.login-form h1 {
  color: var(--color-heading);
  margin-bottom: 0.5rem;
}

.login-form__field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  color: var(--color-text);
  font-size: 0.9rem;
}

.login-form__field input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.95rem;
}

.login-form__field input:focus {
  outline: none;
  border-color: var(--color-border-hover);
}

.login-form__error {
  color: #e04444;
  font-size: 0.9rem;
}

.login-form__submit {
  margin-top: 0.5rem;
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 6px;
  background: var(--color-chrome-background);
  color: var(--color-chrome-text);
  font-weight: 600;
  cursor: pointer;
}

.login-form__submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
