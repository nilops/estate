/*global dispatch*/
import axios from "axios"
import * as messages from "./messages"

export function login(user, pass) {
    dispatch({ type: "START_LOGIN"})
    const req = axios.post(`/api/token/`, {username: user, password: pass})
    req.then((res) => {
        dispatch({
            type: "FINISH_LOGIN",
            payload: res.data,
        })
    }, (err) => {
        dispatch({
            type: "FINISH_LOGIN",
            payload: {token: null}
        })
        messages.handleResponseError(err)
    })
    return req
}
