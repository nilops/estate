import { set } from "lodash/fp"
import { createReducer } from "./utils"
import axios from "axios"

var initialState = {
    authenticating: false,
    token: localStorage.authToken || null,
}

export default createReducer(initialState, {
    ["START_LOGIN"]: (state, action) => {
        state = set(["authenticating"])(true)(state)
        return state
    },

    ["FINISH_LOGIN"]: (state, action) => {
        state = set(["authenticating"])(false)(state)
        state = set(["token"])(action.payload.token)(state)
        if (action.payload.token) {
            localStorage.authToken = action.payload.token
            axios.defaults.headers = {'Authorization': 'Token ' + action.payload.token}
        }
        return state
    },

    ["CONFIRM_LOGIN"]: (state, action) => {
        state = set(["authenticating"])(false)(state)
        state = set(["token"])(action.payload.token)(state)
        axios.defaults.headers = {'Authorization': 'Token ' + action.payload.token}
        return state
    },

    ["DO_LOGOUT"]: (state, action) => {
        state = set(["authenticating"])(false)(state)
        state = set(["token"])(null)(state)
        localStorage.removeItem("authToken")
        axios.defaults.headers = {}
        return state
    },

    ["CONFIRM_LOGOUT"]: (state, action) => {
        state = set(["authenticating"])(false)(state)
        state = set(["token"])(null)(state)
        axios.defaults.headers = {}
        return state
    },
})
