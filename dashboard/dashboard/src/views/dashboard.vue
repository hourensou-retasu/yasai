<template>
  <div class="dashboard container">
    <div class="field is-horizontal">
      <div class="field-body">
        <div class="field">
          <p class="control is-expanded has-icons-right">
            <input
              v-model="syncFreeeYear"
              class="input"
              type="text"
            >
            <span class="icon is-small is-right">
              年
            </span>
          </p>
        </div>
        <div class="field">
          <p class="control is-expanded has-icons-right">
            <input
              v-model="syncFreeeMonth"
              class="input"
              type="text"
            >
            <span class="icon is-small is-right">
              月
            </span>
          </p>
        </div>
        <div class="field">
          <button
            class="button"
            @click.prevent="syncFreee"
          >
            従業員データを更新する
          </button>
        </div>
      </div>
    </div>
    <table class="table is-hoverable is-fullwidth">
      <thead>
        <tr>
          <th class="has-text-centered">
            従業員ID
          </th>
          <th class="has-text-centered">
            姓
          </th>
          <th class="has-text-centered">
            名
          </th>
          <th class="has-text-centered">
            画像
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="user in users"
          :key="user.employee_id"
        >
          <th class="has-text-centered">
            {{ user.employee_id }}
          </th>
          <td class="has-text-centered">
            {{ user.last_name_kanji }}
          </td>
          <td class="has-text-centered">
            {{ user.first_name_kanji }}
          </td>
          <td>
            <img
              v-if="user.img_url"
              class="employee-img image"
              :src="user.img_url"
              :alt="user.employee_id"
            >
            <div
              v-else
              class="file"
            >
              <label class="file-label">
                <input
                  :key="'photo' + user.img_url"
                  class="file-input"
                  type="file"
                  name="resume"
                  @change="setProfilePhoto(user.employee_id, $event)"
                >
                <span class="file-cta">
                  <span class="file-icon">
                    <i class="far fa-image" />
                  </span>
                  <span class="file-label">
                    画像を選択してください
                  </span>
                </span>
              </label>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style lang='scss'>
table.table td, table.table th {
  vertical-align: middle;
}
.employee-img {
  height: 10em;
  margin: 0 auto;
}

.input.set-year {
  width: 3.5em;
}
.input.set-month {
    width: 2em;
}
.file-label {
  margin: 0 auto;
}
</style>

<script>
import { db, storage } from '@/config/firestore';
import axios from 'axios';

const companyID = '1931049'

export default {
  name: 'Dashboard',
  data() {
    return {
      syncFreeeYear: new Date().getFullYear(),
      syncFreeeMonth: new Date().getMonth() + 1,
      users: [],
    };
  },
  firestore: {
    users: db.collection(companyID).orderBy('employee_id'),
  },
  mounted() {
    this.accessToken = localStorage.accessToken
    this.refreshToken = localStorage.refreshToken
  },
  methods: {
    async syncFreee() {
      // freeeAPIから従業員情報を取得
      let res 
      
      try {
        res = await axios.get(
          `https://api.freee.co.jp/hr/api/v1/employees?company_id=${ companyID }&year=${ this.syncFreeeYear }&month=${ this.syncFreeeMonth }`,
          {
            headers: {
              'Authorization': `Bearer ${ this.accessToken }`
            }
          }
        )
      } catch {
        const { access_token, refresh_token } = await this.doRefreshToken()
        this.accessToken = access_token
        localStorage.setItem('accessToken', access_token)
        this.refreshToken = refresh_token
        localStorage.setItem('refreshToken', refresh_token)
        

        res = await axios.get(
          `https://api.freee.co.jp/hr/api/v1/employees?company_id=${ companyID }&year=${ this.syncFreeeYear }&month=${ this.syncFreeeMonth }`,
          {
            headers: {
              'Authorization': `Bearer ${ this.accessToken }`
            }
          }
        )
      }

      console.log(this.accessToken, this.refreshToken)

      const freeeUser = res.data.employees.sort((a, b) => {
        return a.id - b.id
      })

      console.log(freeeUser)

      // 現在のusersに入っていないデータをfirestoreに追加する
      let freeeUserCur = 0
      let firestoreUserCur = 0
      const dbAddStack = []

      const formatUserInfo = employee => {
        return {
          'employee_id': employee.id,
          'first_name_kana': employee.profile_rule.first_name_kana,
          'first_name_kanji': employee.profile_rule.first_name,
          'last_name_kana': employee.profile_rule.last_name_kana,
          'last_name_kanji':employee.profile_rule.last_name
        }
      }

      while(true) {
        if(firestoreUserCur === this.users.length) {
          dbAddStack.push(...freeeUser.slice(freeeUserCur).map(formatUserInfo))
          break
        }
        if(freeeUserCur === freeeUser.length) break

        const employee = freeeUser[freeeUserCur]
        
        if (employee.id === this.users[firestoreUserCur].employee_id) {
          firestoreUserCur++
          freeeUserCur++
        } else if(employee.id < this.users[firestoreUserCur].employee_id) {
          dbAddStack.push(formatUserInfo(employee))
          freeeUserCur++
        } else {
          firestoreUserCur++
        }
      }

      console.log(dbAddStack)

      dbAddStack.forEach(item => {
        db.collection(companyID).doc(String(item.employee_id)).set(item)
      })

    },
    async doRefreshToken() {
      const url = "http://localhost:8000/token"
      const res = await axios.put(url, {
        refreshToken: this.refreshToken
      })
      return res.data
    },
    async setProfilePhoto(employeeID, e) {
      // 画像ファイルを開くローカルで
      const localPhotoFile = e.target.files[0]

      // 画像アップロード
      const newPhotoRef = storage.ref().child(new Date().getTime() + localPhotoFile.name)
      await newPhotoRef.put(localPhotoFile)

      // firebaseにURLを追加する
      db.collection(companyID).doc(String(employeeID)).update({
        'img_url': await newPhotoRef.getDownloadURL()
      })

    }
  }
};
</script>
