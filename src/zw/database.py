import records
import uuid

import zw.logger as logger

LOG = logger.getLogger(__name__)
class Database():
	DB_INIT_SQL = {
		'sqlite': [
			"""CREATE TABLE IF NOT EXISTS ippool (id INTEGER PRIMARY KEY AUTOINCREMENT
				, ip TEXT, port TEXT, country TEXT, city TEXT, speed FLOAT, valid INT DEFAULT 0
				, conn_type TEXT, update_time TIMESTAMP NOT NULL DEFAULT 
				(datetime(CURRENT_TIMESTAMP,'localtime')) )"""
			, """CREATE TRIGGER IF NOT EXISTS update_timestamp AFTER UPDATE ON ippool 
				FOR EACH ROW WHEN NEW.update_time < datetime(CURRENT_TIMESTAMP,'localtime') 
				BEGIN UPDATE ippool SET update_time=datetime(CURRENT_TIMESTAMP,'localtime') WHERE id=OLD.id; END;"""
		]
		, 'mysql': [
			"""CREATE TABLE IF NOT EXISTS ippool (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT
				, ip TEXT, port TEXT, country TEXT, city TEXT, speed FLOAT, valid INT DEFAULT 0
				, conn_type TEXT, update_time TIMESTAMP NOT NULL DEFAULT 
				CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)""",
			"""
			CREATE TABLE IF NOT EXISTS `factiva_by_region` (
			`uid` char(36) NOT NULL,
			`name` varchar(128) NOT NULL,
			`region` varchar(128) NOT NULL,
			`sub_region` varchar(128) NOT NULL,
			`country` varchar(128) NOT NULL,
			`district` varchar(128) NOT NULL,
			`raw_text` text DEFAULT NULL,
			`description` text DEFAULT NULL,
			`source_code` varchar(128) NOT NULL,
			`language` varchar(128) NOT NULL,
			`frequecy` varchar(128) NOT NULL,
			`link` varchar(1024) DEFAULT NULL,
			`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
			`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			`delete_flag` int(11) NOT NULL DEFAULT '0',
			PRIMARY KEY (`uid`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			""",
			"""
			CREATE TABLE IF NOT EXISTS `factiva_by_industry` (
			`uid` char(36) NOT NULL,
			`name` varchar(128) NOT NULL,
			`cata0` varchar(128) NOT NULL,
			`cata1` varchar(128) NOT NULL,
			`cata2` varchar(128) NOT NULL,
			`cata3` varchar(128) NOT NULL,
			`cata4` varchar(128) NOT NULL,
			`cata5` varchar(128) NOT NULL,
			`cata6` varchar(128) NOT NULL,
			`cata7` varchar(128) NOT NULL,
			`raw_text` text DEFAULT NULL,
			`link` varchar(1024) DEFAULT NULL,
			`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
			`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			`delete_flag` int(11) NOT NULL DEFAULT '0',
			PRIMARY KEY (`uid`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			""",
			"""
			CREATE TABLE IF NOT EXISTS `factiva_cata_industry` (
			`uid` char(36) NOT NULL,
			`cata0` varchar(128) NOT NULL,
			`cata1` varchar(128) NOT NULL,
			`cata2` varchar(128) NOT NULL,
			`cata3` varchar(128) NOT NULL,
			`cata4` varchar(128) NOT NULL,
			`cata5` varchar(128) NOT NULL,
			`cata6` varchar(128) NOT NULL,
			`cata7` varchar(128) NOT NULL,
			`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
			`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			`delete_flag` int(11) NOT NULL DEFAULT '0',
			PRIMARY KEY (`uid`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			""",
			"""
			CREATE TABLE IF NOT EXISTS `factiva_cata_expert` (
			`uid` char(36) NOT NULL,
			`cata0` varchar(128) NOT NULL,
			`cata1` varchar(128) NOT NULL,
			`cata2` varchar(128) NOT NULL,
			`cata3` varchar(128) NOT NULL,
			`cata4` varchar(128) NOT NULL,
			`cata5` varchar(128) NOT NULL,
			`cata6` varchar(128) NOT NULL,
			`cata7` varchar(128) NOT NULL,
			`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
			`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			`delete_flag` int(11) NOT NULL DEFAULT '0',
			PRIMARY KEY (`uid`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			""",
			"""
			CREATE TABLE IF NOT EXISTS `factiva_cata_news` (
			`uid` char(36) NOT NULL,
			`cata0` varchar(128) NOT NULL,
			`cata1` varchar(128) NOT NULL,
			`cata2` varchar(128) NOT NULL,
			`cata3` varchar(128) NOT NULL,
			`cata4` varchar(128) NOT NULL,
			`cata5` varchar(128) NOT NULL,
			`cata6` varchar(128) NOT NULL,
			`cata7` varchar(128) NOT NULL,
			`create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
			`update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
			`delete_flag` int(11) NOT NULL DEFAULT '0',
			PRIMARY KEY (`uid`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8;
			"""
		]
	}
	DB_SQL = {
		'ippool_all': 'SELECT id,ip,port,country,city,speed,valid,conn_type,update_time FROM ippool ORDER BY speed ASC'
		, 'ippool_count': 'SELECT count(*) as c, sum(case when valid=100 then 1 else 0 end) as s, sum(case when valid=0 then 1 else 0 end) as f FROM ippool'
		, 'ippool_exist': 'SELECT count(*) AS c FROM ippool WHERE ip=:ip AND port=:port'
		, 'ippool_insert': 'INSERT INTO ippool (ip, port, country, city, speed, conn_type) VALUES(:ip, :port, :country, :city, :speed, :conn_type)'
		, 'ippool_update': 'UPDATE ippool SET country=:country, city=:city, speed=:speed, conn_type=:conn_type WHERE ip=:ip AND port=:port'
		, 'ippool_update_valid': 'UPDATE ippool SET valid=:valid WHERE id=:id'
		, 'spider_factiva_all': 'SELECT * FROM factiva_by_region ORDER BY create_time DESC LIMIT 500'
		, 'spider_factiva_region_check': 'SELECT count(*) AS c FROM factiva_by_region WHERE region=:region and sub_region=:sub_region and country=:country and district=:district and name=:name'
		, 'spider_factiva_region_insert': 'INSERT INTO factiva_by_region (uid, name, region, sub_region, country, district, raw_text, description, source_code, language, frequecy, link) VALUES (:uid, :name, :region, :sub_region, :country, :district, :raw_text, :description, :source_code, :language, :frequecy, :link)'
		, 'spider_factiva_region_update': 'UPDATE factiva_by_region SET name=:name, region=:region, sub_region=:sub_region, country=:country, district=:district, raw_text=:raw_text, description=:description, source_code=:source_code, language=:language, frequecy=:frequecy, link=:link WHERE region=:region and sub_region=:sub_region and country=:country and district=:district and name=:name'
		, 'spider_factiva_cata_industry_insert': 'INSERT INTO factiva_cata_industry (uid, cata0, cata1, cata2, cata3, cata4, cata5, cata6, cata7) VALUES (:uid, :cata0, :cata1, :cata2, :cata3, :cata4, :cata5, :cata6, :cata7)'
		, 'spider_factiva_cata_expert_insert': 'INSERT INTO factiva_cata_expert (uid, cata0, cata1, cata2, cata3, cata4, cata5, cata6, cata7) VALUES (:uid, :cata0, :cata1, :cata2, :cata3, :cata4, :cata5, :cata6, :cata7)'
		, 'spider_factiva_cata_news_insert': 'INSERT INTO factiva_cata_news (uid, cata0, cata1, cata2, cata3, cata4, cata5, cata6, cata7) VALUES (:uid, :cata0, :cata1, :cata2, :cata3, :cata4, :cata5, :cata6, :cata7)'
		, 'spider_factiva_by_industry_insert': 'INSERT INTO factiva_by_industry (uid, name, cata0, cata1, cata2, cata3, cata4,  cata5, cata6, cata7, raw_text, link) VALUES (:uid, :name, :cata0, :cata1, :cata2, :cata3, :cata4, :cata5, :cata6, :cata7, :raw_text, :link)'

	}
	DB_CFG_DEF = None
	def __init__(self, o=None, set_cfg_def=True):
		o = Database.DB_CFG_DEF if o is None else o
		self.db_cfg = o
		self.dbtype = o['dbtype']
		self.dbname = o['dbname']
		self.dbuser = o['dbuser']
		self.dbpass = o['dbpass']
		self.dbaddr = o['dbaddr']
		self.db = None
		Database.DB_CFG_DEF = o if set_cfg_def else Database.DB_CFG_DEF
	
	def init_db(self):
		if self.db is not None:
			self.close()
		self.db = db = self.get_db()
		sqls = Database.DB_INIT_SQL[self.dbtype]
		for sql in sqls:
			#LOG.debug(sql)
			t = db.transaction()
			db.query(sql)
			t.commit()
	
	def get_db(self):
		if self.db is None:
			if 'sqlite' == self.dbtype:
				db = records.Database('sqlite:///%s' % self.dbname)
			elif 'mysql' == self.dbtype:
				db = records.Database('mysql+pymysql://%s:%s@%s/%s?charset=utf8' % (self.dbuser, self.dbpass, self.dbaddr, self.dbname))
			self.db = db
		return self.db
	
	def query(self, op, **params):
		sql = Database.DB_SQL[op]
		db = self.get_db()
		# LOG.debug(sql)
		rows = db.query(sql, **params)
		return rows
	
	def bulk_query(self, op, *multiparams):
		sql = Database.DB_SQL[op]
		db = self.get_db()
		# LOG.debug(sql)
		rows = db.bulk_query(sql, *multiparams)
		return rows
	
	def insert(self, recs, insertop):
		db = self.get_db()
		recs_insert = []
		for r in recs:
			if 'uid' in r and r['uid'] is None:
				r['uid'] = str(uuid.uuid4())
			recs_insert.append(r)
		db.bulk_query(Database.DB_SQL[insertop], *recs_insert)

	def insert_update(self, recs, checkop, insertop, updateop, checkflds):
		db = self.get_db()
		recs_insert = []
		recs_update = []
		for r in recs:
			if 'uid' in r and r['uid'] is None:
				r['uid'] = str(uuid.uuid4())
			flds = {}
			for f in checkflds:
				flds[f] = r[f]
			rs = db.query(Database.DB_SQL[checkop], **flds)
			if rs[0].c == 0:
				recs_insert.append(r)
			else:
				recs_update.append(r)
		LOG.debug( 'Insert: %s, Update: %s' %(len(recs_insert), len(recs_update)) )
		if len(recs_insert)>0:
			db.bulk_query(Database.DB_SQL[insertop], *recs_insert)
		if len(recs_update)>0:
			db.bulk_query(Database.DB_SQL[updateop], *recs_update)
		return len(recs_insert), len(recs_update)
	
	def close(self):
		self.db.close()
		self.db = None
