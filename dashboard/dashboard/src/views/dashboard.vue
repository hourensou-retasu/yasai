<template>
  <div class="dashboard">
    <table>
      <tr>
        <th>employee_id</th>
        <th>last_name_kanji</th>
        <th>first_name_kanji</th>
        <th>img</th>
      </tr>
      <tr
        v-for="user in users"
        :key="user.employee_id"
      >
        <td>{{ user.employee_id }}</td>
        <td>{{ user.last_name_kanji }}</td>
        <td>{{ user.first_name_kanji }}</td>
        <td>
          <img
            v-if="user.img_url"
            class="employee-img"
            :src="user.img_url"
            :alt="user.employee_id"
          >
          <input
            v-else
            :key="'photo' + user.img_url"
            type="file"
            @change="setProfilePhoto(user.employee_id, $event)"
          >
        </td>
      </tr>
    </table>
    <input
      v-model="syncFreeeYear"   
      type="text"
    >
    <input
      v-model="syncFreeeMonth"
      type="text"
    >
    <button
      @click.prevent="syncFreee"
    >
      従業員データを更新する
    </button>
  </div>
</template>

<style lang='scss'>
.employee-img {
  height: 10em;
}
</style>

<script>
import { db, storage } from '@/config/firestore';
import axios from 'axios';

const companyID = '1931049'
const accessToken = '5c54e9a3d5c564ecf94872b185996ae0ac38fc4a89bbb1bfadbdab705dd1e2ad'

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
  methods: {
    async syncFreee() {
      // freeeAPIから従業員情報を取得
      const res = await axios.get(
        `https://api.freee.co.jp/hr/api/v1/employees?company_id=${ companyID }&year=${ this.syncFreeeYear }&month=${ this.syncFreeeMonth }`,
        {
          headers: {
            'Authorization': `Bearer ${ accessToken }`
          }
        }
      )

      const freeeUser = res.data.employees

      console.log(freeeUser)

      // 現在のusersに入っていないデータをfirestoreに追加する
      let freeeUserCur = 0
      let firestoreUserCur = 0
      const dbAddStack = []

      while(true) {
        if(firestoreUserCur === this.users.length) {
          dbAddStack.push(...freeeUser.slice(freeeUserCur))
          break
        }
        if(freeeUserCur === freeeUser.length) break

        const employee = freeeUser[freeeUserCur]
        
        if (employee.id === this.users[firestoreUserCur].employee_id) {
          firestoreUserCur++
          freeeUserCur++
        } else if(employee.id < this.users[firestoreUserCur].employee_id) {
          dbAddStack.push({
            'employee_id': employee.id,
            'first_name_kana': employee.profile_rule.first_name_kana,
            'first_name_kanji': employee.profile_rule.first_name,
            'last_name_kana': employee.profile_rule.last_name_kana,
            'last_name_kanji':employee.profile_rule.last_name
          })
          freeeUserCur++
        } else {
          firestoreUserCur++
        }
      }

      console.log(dbAddStack)

      dbAddStack.forEach(item => {
        db.collection(companyID).add(item)
      })

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
