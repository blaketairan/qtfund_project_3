"""
股票行情数据查询路由模块

提供从TimescaleDB查询历史数据的接口
"""

from flask import Blueprint, request
from app.utils.responses import (
    create_stock_data_response, 
    create_error_response,
    create_success_response,
    format_stock_price_data,
    validate_date_range,
    validate_symbol_format
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
stock_price_bp = Blueprint('stock_price', __name__)


@stock_price_bp.route('/query', methods=['GET', 'POST'])
def query_from_database():
    """从TimescaleDB查询股票行情数据"""
    try:
        # 获取请求参数
        if request.method == 'POST':
            data = request.get_json() or {}
            symbol = data.get('symbol', '')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            limit = data.get('limit', 100)
        else:
            symbol = request.args.get('symbol', '')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            limit = request.args.get('limit', 100, type=int)
        
        # 验证参数
        if not symbol:
            return create_error_response(400, "股票代码不能为空")
        
        symbol = validate_symbol_format(symbol)
        date_range = validate_date_range(start_date, end_date)
        
        if limit <= 0 or limit > 10000:
            return create_error_response(400, "数据条数限制应在1-10000之间")
        
        # 查询数据库
        from app.services.stock_data_service import StockDataService
        service = StockDataService()
        
        db_result = service.query_stock_data_from_db(
            symbol=symbol,
            start_date=date_range['start_date'],
            end_date=date_range['end_date'],
            limit=limit
        )
        
        if not db_result['success']:
            return create_error_response(
                500, 
                "数据库查询失败", 
                db_result.get('error', '未知错误')
            )
        
        # 格式化响应
        stock_data = [format_stock_price_data(record) for record in db_result['data']]
        
        # 计算日期范围
        actual_date_range = None
        if stock_data:
            dates = [item['trade_date'] for item in stock_data]
            actual_date_range = {
                "start": min(dates),
                "end": max(dates),
                "count": len(stock_data)
            }
        
        return create_stock_data_response(
            data=stock_data,
            symbol=symbol,
            source="database",
            date_range=actual_date_range,
            total=db_result['total']
        )
        
    except ValueError as e:
        return create_error_response(400, "参数错误", str(e))
    except Exception as e:
        logger.error(f"数据库查询异常: {e}")
        return create_error_response(500, "查询失败", str(e))


@stock_price_bp.route('/info/<symbol>', methods=['GET'])
def get_stock_info(symbol: str):
    """获取股票基础信息"""
    try:
        symbol = validate_symbol_format(symbol)
        
        from app.services.stock_data_service import StockDataService
        service = StockDataService()
        
        result = service.get_stock_info_from_db(symbol)
        
        if result['success']:
            return create_success_response(
                data=result['data'],
                message="查询成功"
            )
        else:
            return create_error_response(
                404,
                "未找到股票信息",
                result.get('error', '未知错误')
            )
            
    except ValueError as e:
        return create_error_response(400, "参数错误", str(e))
    except Exception as e:
        logger.error(f"查询股票信息异常: {e}")
        return create_error_response(500, "查询失败", str(e))


@stock_price_bp.route('/list', methods=['GET'])
def list_stocks():
    """列出所有股票（包含最新价格信息和可选的脚本计算结果）"""
    try:
        market_code = request.args.get('market_code')
        is_active = request.args.get('is_active', 'Y')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 限制最大查询数量，防止性能问题
        if limit > 10000:
            return create_error_response(
                400,
                "参数错误",
                "limit参数不能超过10000，建议使用分页查询"
            )
        
        if limit <= 0:
            return create_error_response(400, "参数错误", "limit必须大于0")
        
        if offset < 0:
            return create_error_response(400, "参数错误", "offset不能为负数")
        
        from app.services.stock_data_service import StockDataService
        service = StockDataService()
        
        # 使用新方法获取包含价格数据的股票列表
        result = service.list_stocks_with_latest_price(
            market_code=market_code,
            is_active=is_active,
            limit=limit,
            offset=offset
        )
        
        if not result['success']:
            return create_error_response(
                500,
                "查询失败",
                result.get('error', '未知错误')
            )
        
        # 解析并处理 script_ids 参数
        script_ids_param = request.args.getlist('script_ids')
        stocks = result['data']
        
        if script_ids_param:
            try:
                # 转换并验证为整数数组
                script_ids = [int(sid) for sid in script_ids_param]
                
                # 限制数量防止滥用
                if len(script_ids) > 50:
                    return create_error_response(400, "参数错误", "Too many scripts requested")
                
                # 执行脚本
                from app.services.sandbox_executor import SandboxExecutor
                from app.models.custom_script import CustomScript
                from database.connection import db_manager
                
                # 加载脚本
                with db_manager.get_session() as session:
                    scripts = session.query(CustomScript).filter(
                        CustomScript.id.in_(script_ids)
                    ).all()
                    
                    found_ids = {s.id for s in scripts}
                    missing_ids = set(script_ids) - found_ids
                    
                    if missing_ids:
                        return create_error_response(
                            404,
                            "脚本不存在",
                            f"Script IDs not found: {list(missing_ids)}"
                        )
                    
                    scripts_dict = {s.id: s.code for s in scripts}
                
                # 为每只股票执行脚本
                executor = SandboxExecutor()
                for stock in stocks:
                    script_results = {}
                    
                    for script_id, script_code in scripts_dict.items():
                        try:
                            logger.info(f"Executing script {script_id} for stock {stock.get('symbol')}")
                            script_result, error = executor.execute(script_code, context={'row': stock})
                            logger.info(f"Script {script_id} result: {script_result}, error: {error}")
                            script_results[str(script_id)] = script_result if error is None else None
                        except Exception as e:
                            logger.error(f"Script {script_id} execution error for {stock.get('symbol')}: {e}")
                            import traceback
                            logger.error(f"Traceback: {traceback.format_exc()}")
                            script_results[str(script_id)] = None
                    
                    stock['script_results'] = script_results
                
                logger.info(f"Executed {len(scripts_dict)} scripts for {len(stocks)} stocks")
            
            except json.JSONDecodeError:
                return create_error_response(400, "参数错误", "Invalid script_ids JSON format")
            except ValueError as e:
                return create_error_response(400, "参数错误", f"Invalid script_ids: {str(e)}")
            except Exception as e:
                logger.error(f"Script execution error: {e}")
                return create_error_response(500, "脚本执行失败", str(e))
        
        return create_success_response(
            data=stocks,
            total=result['total'],
            message=f"查询到 {result['count']} 只股票"
        )
            
    except Exception as e:
        logger.error(f"列出股票异常: {e}")
        return create_error_response(500, "查询失败", str(e))

