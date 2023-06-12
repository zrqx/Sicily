const { response } = require('express')
const express = require('express')
const mongoose = require('mongoose')
const multer = require('multer')
const path = require('path')

const app = express()

mongoose.connect("mongodb+srv://sicily-admin:scwoKS2Ty9oS2Cks@cluster0.dy2u97a.mongodb.net/?retryWrites=true&w=majority",{useNewUrlParser:true,useUnifiedTopology:true})
// || "mongodb://localhost:27017/testdb"
const db = mongoose.connection
db.on('error', error => console.log(error));
db.once('open', () => {console.log('Connected to Mongoose')})

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'Images')
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname))
    }
})

const upload = multer({storage: storage})

app.use(express.json())

const port = process.env.PORT || 3000
const User = require('./models/user')
const Book = require('./models/book')
const Transaction = require('./models/transaction')
const { format } = require('path')

// Ping

app.get('/ping',(req,res) => {
    res.send('pong')
})

// Users

app.get('/users/:usn',async (req, res) => {
    let response = await User.where('usn').equals(req.params.usn)
    res.send(response[0])
})

app.put('/users/:usn', async (req, res) => {
    let response = await User.findOneAndUpdate(
        {'usn':req.params.usn}, 
        {$set:{'books':req.body.books}}
        )
    res.send(response)
})

app.post('/users', async (req,res) => {
    let response = await User.create({usn: req.body.usn})
    res.send(response)
})

// Books

app.get('/books/:bookId',async (req, res) => {
    let response = await Book.where('bookId').equals(req.params.bookId)
    try {
        if (response != null) {
            res.send(response[0])
        }
    } catch {
        res.sendStatus(404)
    }
})

app.post('/books', async (req, res) => {
    let {bookId, title, author, description} = req.body
    let response = await Book.create({
        bookId,
        title,
        author,
        description
    })
    res.send(response)
})

// Transactions

app.get('/transactions/:from',async (req, res) => {
    let response = await Transaction.where('from').equals(req.params.from)
    res.send(response)
})

app.post('/transactions', async (req, res) => {
    let {transactionType, from, books} = req.body
    // Save Transaction Data
    let response = await Transaction.create({transactionType,from,books})

    // Retrieve User Info
    let user = await User.where('usn').equals(from)

    // Update the User
    if (transactionType == "Issue"){
        await User.findOneAndUpdate({'usn':from}, {$set:{'balance':user[0]["balance"] - req.body.books.length, 'books': books}})
    } else {
        await User.findOneAndUpdate({'usn':from}, {$set:{'balance':user[0]["balance"] + req.body.books.length, 'books': books}})
    }
    
    res.send(response)
})

// File Upload - Authorisation

app.post('/auth', upload.single("image"), (req, res) => {
    res.send(req.file)
})

app.listen(port, () => {
	console.log(`Listening on port ${port}`)
})