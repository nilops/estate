import React from "react"
import { connect } from "react-redux"
import { NavLink, Link } from "react-router-dom"
import Search from "./Search"

class Nav extends React.Component {
    render () {
        return (
            <nav className="navbar navbar-inverse navbar-fixed-top">
                <div className="navbar-header">
                    <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span className="sr-only">Toggle navigation</span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                        <span className="icon-bar"></span>
                    </button>
                    <NavLink className="navbar-brand" to="/"> Estate </NavLink>
                </div>
                <div id="navbar" className="collapse navbar-collapse">
                    <ul className="nav navbar-nav">
                        <li><NavLink className="item" to="/terraform/templates">Templates</NavLink></li>
                        <li><NavLink className="item" to="/terraform/namespaces">Namespaces</NavLink></li>
                        <li><a href="/api/"> API Docs </a></li>
                        <li><a href="/admin/"> Administration </a></li>
                    </ul>
                    <div className="navbar-form navbar-right" style={{marginRight: "1%"}}>
                        <Search />
                        {this.props.token ? <div className="btn btn-default" style={{marginLeft: "10px"}} onClick={this.props.logout}>Logout</div> : null }
                    </div>
                </div>
            </nav>
        )
    }
}

let mapStateToProps = (state) => {
    return {
        token: state.auth.token,
    }
}

let mapDispatchToProps = (dispatch, ownProps) => {
    return {
        logout: () => {
            dispatch({type: "DO_LOGOUT"})
        },
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Nav)
