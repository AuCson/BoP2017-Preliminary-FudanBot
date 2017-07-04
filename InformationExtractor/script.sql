use bop;
create table RELATION(
	page varchar(40),
    subject varchar(40),
    predicate varchar(40),
    object varchar(400),
	time varchar(40),
    org varchar(40),
    person varchar(40),
    num varchar(40),
    origin varchar(400)
)

load data infile 'E:\\Courses\\BOP2017\\Preliminary\\InformationExtractor\\res\\ie.csv'
into table RELATION
fields terminated by ','
lines terminated by '\r\n';