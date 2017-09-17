import React from "react"
import Diff from "react-diff"
import Modal from "./Modal"


export default class ConfirmModal extends React.Component {
    getResult() {
        return {}
    }
    render() {
        return(
            <Modal
                className={this.props.className}
                buttonText={this.props.buttonText}
                titleText={this.props.titleText}
                tooltipText={this.props.tooltipText}
                tooltipDelay={this.props.tooltipDelay}
                disabled={this.props.disabled}
                getResult={this.getResult.bind(this)}
                performLoad={this.props.load}
                performSubmit={this.props.callback}
            >
                <Diff inputA={this.props.diff_old || ""} inputB={this.props.diff_new || ""} type={this.props.diff_type || "chars"} />
            </Modal>
        )
    }
}
