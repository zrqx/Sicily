const mongoose = require('mongoose')

const userSchema = new mongoose.Schema({
	usn: {
        type: String,
        required: true
    },
    balance: {
        type: Number,
        require: true,
        default: 6
    },
    books: {
        type: [String],
        require: true
    },
    lastInteracted: {
        type: Date,
        require: true,
        default: () => Date.now()
    }
})

module.exports = mongoose.model('User', userSchema)