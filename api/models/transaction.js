const mongoose = require('mongoose')

const transactionSchema = new mongoose.Schema({
    transactionId: {
        type: Number,
        required: true,
        default: () => Math.floor(Math.random() * 1000000)
    },
    transactionType: {
        type: String,
        required: true
    },
    from: {
        type: String,
        required: true
    },
    books: {
        type: [String],
        required: true
    },
    transactedOn: {
        type: Date,
        require: true,
        default: () => Date.now()
    }
})

module.exports = mongoose.model('Transaction', transactionSchema)