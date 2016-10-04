from cassandra.cluster import Cluster
import os

cluster = Cluster(contact_points=['127.0.0.1'])
session = cluster.connect()
session.set_keyspace("demo")


cql_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts/cassandra/algotrader.cql'))

with open(cql_path) as cql_file:
    for stmt in cql_file.read().split(";"):
        if len(stmt.strip())>0:
            print stmt
            session.execute(stmt)
#
# session.execute("""
#
# insert into users (lastname, age, city, email, firstname) values ('Jones', 35, 'Austin', 'bob@example.com', 'Bob')
#
# """)

result = session.execute("select * from users where lastname='Jones' ")[0]
print result.firstname, result.age