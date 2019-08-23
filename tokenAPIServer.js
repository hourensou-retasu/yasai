const express = require('express')
const axios = require('axios')
const fs = require('fs')
const cors = require('cors')

const app = express()

app.use(cors())

app.route('/token')
  .get(async (req, res, next) => {
    const code = req.query.code
    const payload = JSON.parse(fs.readFileSync('./freeeAPIsecret.json', 'utf8'))
    payload.code = code
    payload.grant_type = 'authorization_code'

    let tokens
    
    try {
      tokens = await axios.post(`https://accounts.secure.freee.co.jp/public_api/token`, payload)
    } catch {
      return res.status(401).json(tokens.data)
    }
    
    console.log(tokens.data)

    res.status(200).json(tokens.data)

    return
  })

app.listen(8000)