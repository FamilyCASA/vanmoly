"""
优惠券模块路由
API端点: /api/v3/coupons
"""
from flask import Blueprint, request, jsonify
from datetime import datetime


coupon_bp = Blueprint('coupon', __name__)


def api_response(code=200, message='success', data=None):
    """统一API响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data,
        'timestamp': int(datetime.utcnow().timestamp())
    }), code


@coupon_bp.route('/coupons', methods=['GET'])
def get_coupons():
    """获取优惠券列表"""
    return api_response(data={'items': [], 'total': 0})


@coupon_bp.route('/coupons', methods=['POST'])
def create_coupon():
    """创建优惠券"""
    return api_response(code=404, message='功能开发中')


@coupon_bp.route('/coupons/<int:coupon_id>/claim', methods=['POST'])
def claim_coupon(coupon_id):
    """领取优惠券（对外接口）"""
    return api_response(code=404, message='功能开发中')


@coupon_bp.route('/coupons/redeem', methods=['POST'])
def redeem_coupon():
    """核销优惠券"""
    return api_response(code=404, message='功能开发中')
