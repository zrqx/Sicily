const mongoose = require('mongoose')

const bookSchema = new mongoose.Schema({
    bookId: {
        type: Number,
        required: true
    },
    title: {
        type: String,
        required: true
    },
    author: {
        type: String,
        required: true
    },
    description: {
        type: String,
        required: true
    }
})

module.exports = mongoose.model('Book', bookSchema)