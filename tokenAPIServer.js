const express = require('express')
const axios = require('axios')
const fs = require('fs')
const cors = require('cors')
const history = require('connect-history-api-fallback')

const staticApp = express()
staticApp.use(history)
staticApp.use(express.static('./dashboard/dashboard/dist'))
// staticApp.listen(8080)

const app = express()

app.use(cors())
app.use(express.json())

app.route('/token')
  .get(async (req, res) => {
    const code = req.query.code
    const payload = JSON.parse(fs.readFileSync('./freeeAPIsecret.json', 'utf8'))
    payload.code = code
    payload.grant_type = 'authorization_code'

    let tokens
    
    tokens = await axios.post(`https://accounts.secure.freee.co.jp/public_api/token`, payload).catch(e => {
      console.log(e)
      return res.status(401).json(tokens.data)
    })
    
    console.log(tokens.data)

    res.status(200).json(tokens.data)

    return
  })
  .put(async (req, res) => {
    const payload = JSON.parse(fs.readFileSync('./freeeAPIsecret.json', 'utf8'))
    payload.refresh_token = req.body.refreshToken
    payload.grant_type = 'refresh_token'

    let tokens

    tokens = await axios.post(`https://accounts.secure.freee.co.jp/public_api/token`, payload).catch(e => {
      console.log(e)
      return res.status(401).json(tokens.data)
    })

    console.log(tokens.data)

    return res.status(200).json(tokens.data)

  })

app.listen(8000)
