from config.database import get_connection
conn = get_connection()
cursor = conn.cursor()
cursor.execute("UPDATE campaign_queue SET status = 'pending' WHERE campaign_id = 17")
cursor.execute("UPDATE campaigns SET completed_count = 0, failed_count = 0, pending_count = (SELECT COUNT(*) FROM campaign_queue WHERE campaign_id = 17), status = 'Ready' WHERE id = 17")
conn.commit()
conn.close()
print("Campaign #17 reset to PENDING and READY.")
