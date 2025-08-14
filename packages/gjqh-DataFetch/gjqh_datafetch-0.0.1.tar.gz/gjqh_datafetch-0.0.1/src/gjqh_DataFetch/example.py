
# 需要将DataFetch.cp38-win_amd64.pyd置于本文件的同级目录下。
# pip install clickhouse-connect; pip install pandas

from gjqh_DataFetch import DataFetch
import pandas as pd
import json

# 01 类初始化
# account_id : 资金账号;
# acquire_key : 密码 用于查询数据库 默认123456;
# user_id : 用户名 用于在数据库内进行操作留痕 建议填写

x = DataFetch(account_id='1086000', acquire_key='123456', user_id='yh')


# 02 新增信号/覆盖信号 适用情况：1，当前tradingday首次导入数据 2，当前tradingday下, 某个contract 的持仓量/方向/日盘夜盘等特征 需要修改
# 字段格式要求： 可参考 factors.t_order_dtl 中的字段格式 枚举值需符合规定
# 除 trade_time, signal_date 外 均为必填项

###########
# 更新 
# 对锁 ：平今对锁 数据集 mat_01 增加参数 传入 feature = 1


# 一些更新
# 单次上传只能上传同一个交易日（tradingday 唯一）

### fun_update_signal 函数参数
# 1 continuous_holding 参数：适用于日内某几个合约调仓

# continuous_holding = False : 未上传合约会被平仓
# continuous_holding = True : 同一tradingday下，每个合约取最近一次上传的仓位。当前tradingday下未曾上传的合约不交易。
# input_data 中未传入的合约不交易 ： 需要在调用 fun_update_signal 时候 增加 参数 continous_holding=True （默认continous_holding=False）

# 2 use_redis 参数
# 使用 redis 交易： 需要在调用 fun_update_signal 时候 增加 参数 use_redis=True （默认use_redis=False）
###########



mat_01 = pd.DataFrame(data=[['20230804', 'AP2310', 5, 'L', 'intraday_trading', '', '20230803'],
                            ['20230804', 'AP2311', 5, 'L', 'intraday_trading', 'D', '']],
                      columns=['trading_day', 'contract', 'position', 'direction', 'order_typ', 'trade_time', 'signal_date'])

mat_01 = pd.DataFrame(data=[['20230804', 'AP2310', 5, 'L', 'intraday_trading'],
                            ['20230804', 'AP2311', 5, 'L', 'intraday_trading']],
                      columns=['trading_day', 'contract', 'position', 'direction', 'order_typ'])

mat_02 = json.loads(mat_01.to_json(orient='records'))
a01 = x.fun_update_signal(input_data=mat_02, use_redis=True, continuous_holding=True)


# 03 删除数据
# 仅适用于仿真非redis上传仓位的情况
# 实盘 redis 请使用 fun_update_signal 进行目标仓位调整

a02 = x.fun_delete_signal(trading_day='20230723', trade_time='D', order_typ='intraday_trading', contract=['AP2311'])
a03 = x.fun_delete_signal(trading_day='20230723', trade_time='D', order_typ='intraday_trading')
a041 = x.fun_delete_signal(trading_day='20230804', trade_time='', order_typ='intraday_trading', contract=['AP2310'])


# 04 查询导入的仓位（这里不显示已删除数据）trading_day >= start_date and trading_day <= end_date
a04 = x.fun_read_signal(start_date='20230719', end_date='20230720')


# 05 06 查询时间段内的成交明细以及持仓情况（t+1更新） Factors.t_deal_dtl  m_strTradeDate >= start_date and m_strTradeDate <= end_date
a05 = x.fun_read_deal(start_date='20230721', end_date='20230721')
a06 = x.fun_read_position(start_date='20230721', end_date='20230721')


# 07 更改当前资金账号的交易状态 Factors.t_account_info 生效时间：从当前时间点开始
a07 = x.fun_update_sts(trade_tag='T')


#############
# 20240122更新

# 08 读取当前仓位 （盘中 / 盘后）

a08 = x.fun_redis_position() # 返回的是盘中由持仓查询回调返回的最新仓位。code = 0 即查询成功

#############

# 20240208 更新 

# 09 新增 读取 净值情况

a09 = x.fun_read_equity() # 返回的是历史净值及份额 目前暂不支持时间区间删选 返回的是全量净值情况  
a09 = x.fun_margin_used() # 返回的是实时净值 balance

## 10 因子值查询 
test = DataFetch.factors_value(typ='value', start_date= '20240905', end_date = '20240906')
print(test['data'])

test = DataFetch.factors_value(typ='weight', start_date= '20240905', end_date = '20240906')
print(test['data'])


# 11 拆单 参数自定义 （在redis场景下）
# if_twap 1 : True; 0: False
# time_gap : 相邻报单时间间隔 -- 单位 s
# volume : 拆单手数
## 程序有一个初始值（初始值不区分品种） 可以用下述参数覆盖原始 # 只需要上传一次 之后一直生效 不需要每天上传

df_01 = pd.DataFrame(data=[['SA', 1, 0.5, 5],
                           ['RM', 1, 0.5, 5],
                           ['BU', 1, 0.5, 5],
                           ['P', 1, 0.5, 5],
                           ['I', 1, 0.5, 5],
                           ['Y', 1, 0.5, 5],
                           ['J', 1, 0.5, 5],
                           ['TA', 1, 0.5, 5],
                           ['JM', 1, 0.5, 5],
                           ['MA', 1, 0.5, 5],
                           ['M', 1, 0.5, 5],
                           ['CF', 1, 0.5, 5],
                           ['LU', 1, 0.5, 5],
                           ['RU', 1, 0.5, 5],
                           ['EB', 1, 0.5, 5],
                           ['SR', 1, 0.5, 5],
                           ['FG', 1, 0.5, 5],
                           ['OI', 1, 0.5, 5],
                           ['RB', 1, 0.5, 5],
                           ['HC', 1, 0.5, 5],
                           ],
                      columns=['commodity', 'if_twap', 'time_gap', 'volume'])

df_02 = json.loads(df_01.to_json(orient='records'))
a01 = x.fun_update_TWAP_info(input_data=df_02)

