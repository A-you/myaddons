odoo.define('web_approval.FormRenderer', function (require) {
    var formRenderer = require('web.FormRenderer');
    var core = require('web.core');
    $.extend(formRenderer.prototype.custom_events, {
        update_header_button_state: '_updateHeaderButtonState',
    });
    formRenderer.include({
        // @override
        _renderTagHeader: function (node) {
            var $statusbar = this._super.apply(this, arguments);
            this._renderApprovalButton($statusbar);
            return $statusbar;
        },
        // 更新Header审批相关按钮状态
        _renderApprovalButton: function ($statusbar) {
            var approvalData = this.state.approvalData;
            if(approvalData){
                if(approvalData instanceof Array){
                    approvalData = approvalData[0]
                }
                var buttonState = approvalData.buttonState;
                $statusbar.find('.commit_approval').toggleClass('o_hidden', !buttonState.commit_approval);
                $statusbar.find('.pause_approval').toggleClass('o_hidden', !buttonState.pause_approval);
                $statusbar.find('.resume_approval').toggleClass('o_hidden', !buttonState.resume_approval);
                $statusbar.find('.cancel_approval').toggleClass('o_hidden', !buttonState.cancel_approval);
                // $statusbar.find('.approval').toggleClass('o_hidden', !buttonState.approval);
                // $statusbar.find('.btn-do-swap').toggleClass('o_hidden', !buttonState.approval_swap);

                // this.$('.o_chatter_button_approval').toggleClass('o_hidden', !buttonState.chatter_approval);
            }
        },
        _updateHeaderButtonState: function (odooEvent) {
            var approvalData = odooEvent.data;
            if(approvalData){
                var buttonState = approvalData[0].buttonState;
                this.$('.commit_approval').toggleClass('o_hidden', !buttonState.commit_approval);
                this.$('.pause_approval').toggleClass('o_hidden', !buttonState.pause_approval);
                this.$('.resume_approval').toggleClass('o_hidden', !buttonState.resume_approval);
                this.$('.cancel_approval').toggleClass('o_hidden', !buttonState.cancel_approval);
                // this.$('.approval').toggleClass('o_hidden', !buttonState.approval);
                // this.$('.btn-do-swap').toggleClass('o_hidden', !buttonState.approval_swap);

                // this.$('.o_chatter_button_approval').toggleClass('o_hidden', !buttonState.chatter_approval);
            }
        },
        // _renderView: function () {
        //     var self = this;
        //     return this._super.apply(this, arguments).then(function () {
        //         return self._renderApproval()
        //     })
        // },
        // _renderApproval: function () {
        //     return $.when(this._renderApprovalInfo())
        // },
        // _renderApprovalInfo: function () {
        //
        //
        // },
        _addOnClickAction: function ($el, node) {
            if($el.hasClass('btn-diagram')){
                var self = this;
                $el.click(function () {
                    self.trigger_up('btn_diagram_clicked', {
                        attrs: node.attrs,
                        record: self.state,
                    });
                });
            }
            // else if($el.hasClass('btn-do-swap')){
            //     var self = this;
            //     $el.click(function () {
            //         self.trigger_up('btn_swap_clicked', {
            //             attrs: node.attrs,
            //             record: self.state,
            //         });
            //     });
            // }
            else{
                this._super($el, node)
            }
        },
    })

});