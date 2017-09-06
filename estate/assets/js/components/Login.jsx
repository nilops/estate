import React from "react"
import { connect } from "react-redux"
import { Route } from "react-router-dom"
import * as api from "../api/auth"

class Login extends React.Component {

    handleSubmit(event) {
        event.preventDefault()
        event.stopPropagation()
        this.props.login(this.refs.user.value, this.refs.pass.value)
    }
    render () {
        if (this.props.authenticating){
            return <div> Logging in...</div>
        } else if (this.props.token) {
            return (
                <div>{this.props.children}</div>
            )
        } else {
            return (
                <div className="col-xs-6 col-xs-offset-3 well" style={{marginTop: "20px"}}>
                    <form onSubmit={this.handleSubmit.bind(this)} >
                        <p>Please Login</p>
                        <div className="form-group">
                            <input type="text" ref="user" className="form-control" placeholder="Username"/>
                            <input type="password" ref="pass" className="form-control" placeholder="Password"/>
                            <input type="submit" className="btn btn-default pull-right" aria-label="Left Align" />
                        </div>
                    </form>
                </div>
            )
        }
    }
}

let mapStateToProps = (state) => {
    return {
        authenticating: state.auth.authenticating,
        token: state.auth.token,
    }
}

let mapDispatchToProps = (dispatch, ownProps) => {
    return {
        login: (user, pass) => {
            api.login(user, pass)
        },
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Login)
