"""Seed demo data into gamepulse.db for portfolio presentation."""
import sqlite3
import json
from datetime import datetime, timedelta

DB_PATH = "gamepulse.db"

def ts(offset_hours=0, offset_days=0):
    """Return ISO timestamp: now - offset."""
    t = datetime.utcnow() - timedelta(hours=offset_hours, days=offset_days)
    return t.isoformat() + "Z"

def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM payments")
    conn.execute("DELETE FROM feedbacks")
    conn.execute("DELETE FROM liveops")
    conn.execute("DELETE FROM networks")

    # ── Payments ──
    payments = [
        ("PAY-L0000001", "TW-888888", "TW-99999", "大R_阿豪", "S1-台服",
         "ORD-20260615-A001", "Apple Store (iOS)", 99.99, "台湾", 8, "high",
         ts(2), ts(2), ts(1), 1,
         "玩家反馈648礼包已扣款但道具未到账，App Store已显示扣款成功。玩家为SVIP等级，月消费$500+，要求2小时内处理。",
         "pending", ts(2), None, ""),
        ("PAY-L0000002", "TH-123456", "TH-78901", "Mana_T", "S3-泰服",
         "ORD-20260615-R002", "Razer Gold (东南亚)", 29.99, "泰国", 7, "mid",
         ts(8), ts(8), ts(4), 4,
         "玩家在Razer Gold购买月卡，支付成功但游戏内未激活。提供了Razer Gold交易截图。",
         "progress", ts(8), None, "已联系Razer Gold客服核查，等待交易确认回执。"),
        ("PAY-L0000003", "BR-445566", "BR-77889", "Lucas_Silva", "S2-巴西服",
         "ORD-20260614-G003", "Google Play", 49.90, "巴西", -3, "high",
         ts(4, 1), ts(4, 1), ts(3, 1), 1,
         "巴西玩家购买成长基金未到账，Google Play扣款确认邮件已发。该玩家在Discord社群公开抱怨，需紧急处理。",
         "pending", ts(4, 1), None, ""),
        ("PAY-L0000004", "ID-990011", "ID-22334", "Rama_P", "S5-印尼服",
         "ORD-20260614-C004", "Codashop", 14.99, "印尼", 7, "mid",
         ts(12, 2), ts(12, 2), ts(8, 2), 4,
         "Codashop支付成功后道具延迟约3小时才到账，玩家担心后续充值安全。",
         "done", ts(12, 2), ts(2, 2), "已确认Codashop回调延迟，道具实际已到账。已安抚玩家并补偿500钻石。"),
        ("PAY-L0000005", "PH-332211", "PH-44556", "JuanD_MNL", "S1-菲律宾",
         "ORD-20260613-A005", "Apple Store (iOS)", 19.99, "菲律宾", 8, "mid",
         ts(8, 3), ts(8, 3), ts(4, 3), 4,
         "iOS内购通行证扣款但未解锁，玩家发了App Store收据截图。",
         "progress", ts(8, 3), None, "已提交Apple后台查询，预计48小时内出结果。"),
        ("PAY-L0000006", "VN-778899", "VN-11223", "NguyenM", "S4-越南服",
         "ORD-20260612-G006", "Google Play", 4.99, "越南", 7, "low",
         ts(20, 4), ts(20, 4), ts(4, 4), 24,
         "新手礼包$4.99扣款未到账，玩家发邮件附带Google Play收据。",
         "done", ts(20, 4), ts(12, 4), "已核实Google Play回调记录，道具已手动补发。"),
        ("PAY-L0000007", "KR-554433", "KR-66778", "서울_Player", "S6-韩服",
         "ORD-20260612-M007", "MyCard (台湾)", 89.99, "韩国", 9, "mid",
         ts(3), ts(3), ts(-1), 4,
         "韩国玩家通过MyCard储值，支付成功游戏内未收到钻石。MyCard交易记录已提供。",
         "pending", ts(3), None, ""),
        ("PAY-L0000008", "US-998877", "US-55443", "DarkKnight", "S3-美服",
         "ORD-20260611-CC008", "信用卡直付", 199.99, "美国", -5, "high",
         ts(6, 5), ts(6, 5), ts(5, 5), 1,
         "美国玩家信用卡直付$199.99购买限时礼包，银行已扣款但游戏内未收到。玩家提交了银行账单截图，威胁要发起chargeback。",
         "verified", ts(6, 5), ts(3, 5), "已联系支付网关核实，交易确实成功。待运营确认后手动补发道具。"),
        ("PAY-L0000009", "HK-112244", "HK-33556", "HK_Gamer88", "S7-港服",
         "ORD-20260610-A009", "Apple Store (iOS)", 24.99, "香港", 8, "low",
         ts(10, 6), ts(10, 6), ts(2, 6), 24,
         "iOS月卡续费扣款未到账，玩家发来App Store订阅记录截图。",
         "done", ts(10, 6), ts(5, 6), "已通过iTunes Connect查询到延迟到账记录，月卡已正常激活。玩家确认收到。"),
        ("PAY-L0000010", "TW-336699", "TW-44880", "小雨_台服", "S1-台服",
         "ORD-20260609-G010", "Google Play", 64.99, "台湾", 8, "mid",
         ts(12, 7), ts(12, 7), ts(8, 7), 4,
         "Google Play支付成功，钻石未到账。已提供GP订单号GPA.XXXX-XXXX。",
         "reissued", ts(12, 7), ts(6, 7), "确认Google Play回调异常，已手动补发钻石。玩家确认到账。"),
    ]

    for p in payments:
        conn.execute("""
            INSERT INTO payments (id, char_id, account_id, char_name, server,
                order_id, channel, amount, region, tz, priority,
                report_time, report_local, sla_deadline, sla_hours,
                desc, status, created_at, resolved_at, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, p)

    # ── Feedbacks ──
    feedbacks = [
        ("FB-L0000001", "Discord", "Bug/闪退",
         "TH-123456", "TH-78901", "Mana_T", "S3-泰服", "泰国",
         "新版本v2.7.1更新后，进入战斗画面必闪退。已有多名公会成员反馈同样问题。机型：iPhone 13 Pro Max，iOS 18.5。", "wide", "critical",
         ts(3), "open"),
        ("FB-L0000002", "Reddit", "游戏平衡",
         "", "", "/u/MLGPro360", "", "美国",
         "New hero Aurora is completely broken in PvP. Her ult one-shots the entire team through shields. Basically unplayable if you don't own her. Needs emergency nerf.", "wide", "major",
         ts(6, 1), "open"),
        ("FB-L0000003", "App Store 评论", "充值/支付",
         "TW-336699", "TW-44880", "小雨_台服", "S1-台服", "台湾",
         "这已经是第三次充值扣款没收到道具了！每次都要找客服，体验很差。扣款秒扣，补发要等半天。再这样删游了。App Store 1星评价。", "some", "critical",
         ts(12, 2), "open"),
        ("FB-L0000004", "Facebook", "活动建议",
         "", "", "Rizky_FB", "", "印尼",
         "Kenapa game ini tidak support pembayaran via GoPay/OVO? Banyak player Indonesia yang tidak punya kartu kredit. Minta tambahin opsi pembayaran lokal dong 🙏", "some", "major",
         ts(4, 3), "open"),
        ("FB-L0000005", "Discord", "连接/延迟",
         "BR-445566", "BR-77889", "Lucas_Silva", "S2-巴西服", "巴西",
         "Desde a atualização de ontem, o ping no servidor brasileiro está acima de 200ms. Antes ficava em 30-40ms. Vários jogadores reclamando no Discord. Provavelmente problema de rota CDN.", "wide", "critical",
         ts(8), "open"),
        ("FB-L0000006", "Google Play 评论", "UI/翻译",
         "", "", "VNGamer99", "", "越南",
         "Nhiều đoạn text tiếng Việt bị lỗi font, hiển thị ô vuông thay vì chữ có dấu. Màn hình nâng cấp trang bị bị lỗi hiển thị trên điện thoại màn hình nhỏ.", "some", "minor",
         ts(12, 4), "open"),
        ("FB-L0000007", "客服工单", "内容需求",
         "KR-554433", "KR-66778", "서울_Player", "S6-韩服", "韩国",
         "한국 서버는 왜 다른 지역보다 업데이트가 항상 늦나요? 글로벌 서버와 동시 업데이트를 원합니다. 한국 유저들도 같은 게임을 하고 있어요.", "some", "major",
         ts(4, 5), "open"),
    ]

    for f in feedbacks:
        conn.execute("""
            INSERT INTO feedbacks (id, source, category, char_id, account_id,
                char_name, server, region, content, impact, severity, created_at, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, f)

    # ── LiveOps ──
    liveops = [
        ("LO-L0000001", "端午限时充值返利", "充值活动",
         "2026-06-18T10:00", "2026-06-22T23:59",
         json.dumps(["台湾", "香港"]),
         "充值满$50返10%钻石，满$100返20%。配合端午节日氛围，定制龙舟主题限定头像框。",
         ts(0)),
        ("LO-L0000002", "全球夏日赛季S5", "赛季活动",
         "2026-06-20T08:00", "2026-07-20T08:00",
         json.dumps(["台湾", "泰国", "印尼", "菲律宾", "越南", "巴西", "美国", "韩国", "日本"]),
         "新赛季通行证，夏日限定皮肤x3，每日挑战任务。赛季奖励：传说皮肤'潮汐女武神'。注意各时区开赛时间对齐：UTC+8 08:00 = UTC+7 07:00 = UTC-3 21:00。",
         ts(0)),
        ("LO-L0000003", "Discord社区二创大赛", "社区活动",
         "2026-06-25T12:00", "2026-07-09T12:00",
         json.dumps(["全球"]),
         "Discord频道举办玩家同人创作比赛，前三名奖励限定周边+游戏钻石。评审标准：创意50%、质量30%、社区投票20%。",
         ts(0)),
    ]

    for lo in liveops:
        conn.execute("""
            INSERT INTO liveops (id, name, type, start, "end", regions, note, created_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, lo)

    # ── Networks ──
    networks = [
        ("NET-L0000001", "巴西", "CDN 超时",
         "2026-06-15T14:30", 1200,
         "巴西圣保罗节点CDN回源超时，导致玩家无法进入游戏约45分钟。受影响玩家集中在巴西服S2-S3服务器。已切换备用CDN节点恢复。根因：主CDN节点SSL证书过期未自动续签。",
         ts(4, 1)),
        ("NET-L0000002", "泰国", "延迟/卡顿",
         "2026-06-14T20:00", 300,
         "泰国True ISP用户报告延迟从40ms升至180ms，持续约2小时。Discord上约有50+玩家反馈。可能原因：True ISP国际出口路由临时变更。已通知运维监控。",
         ts(6, 2)),
    ]

    for n in networks:
        conn.execute("""
            INSERT INTO networks (id, region, type, time, affected, desc, created_at)
            VALUES (?,?,?,?,?,?,?)
        """, n)

    conn.commit()
    conn.close()
    print(f"✅ Seeded: {len(payments)} payments, {len(feedbacks)} feedbacks, {len(liveops)} liveops, {len(networks)} networks")

if __name__ == "__main__":
    seed()
