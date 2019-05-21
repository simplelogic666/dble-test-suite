# Copyright (C) 2016-2019 ActionTech.
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher.
Feature: #
  Scenario:  #1 test parameter"sqlMaxLimit" "dataNode" "needAddLimit"in schema.xml
     Given delete the following xml segment
      |file        | parent          | child               |
      |schema.xml  |{'tag':'root'}   | {'tag':'schema'}    |

     Given add xml segment to node with attribute "{'tag':'root'}" in "schema.xml"
      """
      <schema dataNode="dn5" name="mytest" sqlMaxLimit="3">
		    <table dataNode="dn1,dn3" name="test_table" type="global" />
      </schema>
     """
    Then execute admin cmd "reload @@config_all"
    Then execute sql in "dble-1" use "test"
        | user | passwd | conn   | toClose  | sql                                                    | expect      | db     |
        | test | 111111 | conn_0 | False    | drop table if exists test_table                  | success | mytest |
        | test | 111111 | conn_0 | False    | create table test_table(id int)   | success     | mytest |
        | test | 111111 | conn_0 | False    | insert into test_table values(1),(2),(3),(4),(5)| success     | mytest |
        | test | 111111 | conn_0 | False    | drop table if exists default_table                  | success | mytest |
        | test | 111111 | conn_0 | False    | create table default_table(id int)                    | success | mytest |
        | test | 111111 | conn_0 | True     | insert into default_table values(1)/*dest_node:dn5*/    | success | mytest |
    Then get limited results
    """
    3
    """
    #1.2 test parameter "needAddLimit"
    Given delete the following xml segment
      |file        | parent          | child               |
      |schema.xml  |{'tag':'root'}   | {'tag':'schema'}    |

    Given add xml segment to node with attribute "{'tag':'root'}" in "schema.xml"
    """
      <schema dataNode="dn5" name="mytest" sqlMaxLimit="3">
		    <table dataNode="dn1,dn3" name="test_table" type="global" needAddLimit="false"/>
      </schema>
    """
    Then execute admin cmd "reload @@config_all"
    Then get limited results
    """
    5
    """
  Scenario:# when table name has multiple values
     Given add xml segment to node with attribute "{'tag':'schema','kv_map':{'name':'mytest'}}" in "schema.xml"
     """
        <table name="test_table,test2_table" dataNode="dn1,dn2,dn3,dn4" type="global" />
    """
    Then execute admin cmd "reload @@config_all"
    Then execute sql in "dble-1" use "test"
        | user | passwd | conn   | toClose  | sql                                           | expect              | db     |
        | test | 111111 | conn_0 | False    | drop table if exists test_table          | success             | mytest |
        | test | 111111 | conn_0 | False    | create table test_table(id int)          | success             | mytest |
        | test | 111111 | conn_0 | False    | show full tables                            | has{('test_table','BASE TABLE')}   | mytest |
        | test | 111111 | conn_0 | False    | drop table if exists test2_table          | success             | mytest |
        | test | 111111 | conn_0 | False    | create table test2_table(id int)          | success             | mytest |
        | test | 111111 | conn_0 | True    | show full tables                              | has{('test_table','BASE TABLE')}   | mytest |

  Scenario:# dataNode has no related databases
     Given delete the following xml segment
      |file        | parent          | child               |
      |schema.xml  |{'tag':'root'}   | {'tag':'schema'}    |
      |schema.xml  |{'tag':'root'}   | {'tag':'dataNode'}  |
      |schema.xml  |{'tag':'root'}   | {'tag':'dataHost'}  |
     Given add xml segment to node with attribute "{'tag':'root'}" in "schema.xml"
     """
    	<schema dataNode="dn1" name="mytest" sqlMaxLimit="100">
		    <table dataNode="dn1,dn3" name="test" type="global" />
	    </schema>
	    <dataNode dataHost="dh1" database="db1" name="dn1" />
	    <dataNode dataHost="dh1" database="db2" name="dn3" />
	    <dataHost balance="0" maxCon="100" minCon="10" name="dh1" slaveThreshold="100" switchType="-1">
		    <heartbeat>select user()</heartbeat>
		    <writeHost host="hostM1" password="111111" url="172.100.9.5:3306" user="test">
		    </writeHost>
	    </dataHost>
      """
    Given start mysql in host "mysql-master1"
    Then execute sql in "mysql-master1"
        | user | passwd | conn   | toClose  | sql                                           | expect              | db     |
        | test | 111111 | conn_0 | False    | drop database if exists db1         | success             |  |
        | test | 111111 | conn_0 | False    | drop database if exists db2         | success             |  |
        | test | 111111 | conn_0 | False    | drop database if exists db3         | success             |  |
        | test | 111111 | conn_0 | False    | drop database if exists db4         | success             |  |
    Given Restart dble in "dble-1"
    Then execute sql in "mysql-master1"
        | user | passwd | conn   | toClose  | sql                                           | expect              | db     |
        | test | 111111 | conn_0 | False    | create database if not exists db1         | success             |  |
        | test | 111111 | conn_0 | False    | create database if not exists db2         | success             |  |
        | test | 111111 | conn_0 | False    | create database if not exists db3         | success             |  |
        | test | 111111 | conn_0 | False    | create database if not exists db4         | success             |  |

  Scenario:# test parameters "maxCon"
    # test connctions can't more than maxCon
    Given delete the following xml segment
      |file        | parent          | child               |
      |schema.xml  |{'tag':'root'}   | {'tag':'schema'}    |
      |schema.xml  |{'tag':'root'}   | {'tag':'dataNode'}  |
      |schema.xml  |{'tag':'root'}   | {'tag':'dataHost'}  |
    Given add xml segment to node with attribute "{'tag':'root'}" in "schema.xml"
    """
	    <schema dataNode="dn1" name="mytest" sqlMaxLimit="100">
		    <table dataNode="dn1,dn3" name="test" type="global" />
	    </schema>
	    <dataNode dataHost="dh1" database="db1" name="dn1" />
	    <dataNode dataHost="dh1" database="db2" name="dn3" />
	    <dataHost balance="0" maxCon="9" minCon="3" name="dh1" slaveThreshold="100" switchType="-1">
		    <heartbeat>select user()</heartbeat>
		    <writeHost host="hostM1" password="111111" url="172.100.9.5:3306" user="test">
		    </writeHost>
	    </dataHost>
    """
    Then execute admin cmd "reload @@config_all"
    Then create "9" conn
    Then create "10" conn
    """
    can't create connections more than maxCon
    """

  Scenario: # test cache related parameter "primaryKey"
    #1 set primaryKey=id and the primary key of test_table is also id
    Given add xml segment to node with attribute "{'tag':'schema','kv_map':{'name':'mytest'}}" in "schema.xml"
    """
        <table name="test_table" dataNode="dn1,dn2,dn3,dn4" primaryKey="id" rule="hash-two" />
    """
    Then execute admin cmd "reload @@config_all"
    Then execute sql in "dble-1" use "test"
        | user | passwd | conn   | toClose  | sql                                                                  | expect         | db     |
        | test | 111111 | conn_0 | False    |drop table if exists test_table                                   | success       | mytest |
        | test | 111111 | conn_0 | False    |create table test_table(id int primary key,name varchar(20)) |success        | mytest |
        | test | 111111 | conn_0 | False    |insert into test_table values(1,'test1'),(2,'test2')           | success      | mytest |
        | test | 111111 | conn_0 | True     |select * from test_table where name = 'test1'                   | success       | mytest |
    Then execute sql in "dble-1" use "admin"
        | user | passwd | conn   | toClose  | sql                         | expect                             | db     |
        | root | 111111 | conn_0 | True     | show @@cache               | length{(2)}| |
    Then execute sql in "dble-1" use "test"
        | user | passwd | conn   | toClose  | sql                                                                  | expect         | db     |
        | test | 111111 | conn_0 | True     |select * from test_table where id =1                       | success       | mytest |
    Then execute sql in "dble-1" use "admin"
        | user | passwd | conn   | toClose  | sql                         | expect                             | db     |
        | root | 111111 | conn_0 | True     | show @@cache               | match{('TableID2DataNodeCache.`mytest`_`test_table`',10000L,1L,1L,0L,1L,2018')}| |

    #2 set primaryKey=name,but the primary key of test_table is id
    Given add xml segment to node with attribute "{'tag':'schema','kv_map':{'name':'mytest'}}" in "schema.xml"
    """
        <table name="test_table" dataNode="dn1,dn2,dn3,dn4" primaryKey="name" rule="hash-two" />
    """
    Then execute admin cmd "reload @@config_all"
    Then execute sql in "dble-1" use "test"
        | user | passwd | conn   | toClose  | sql                                                                  | expect         | db     |
        | test | 111111 | conn_0 | True     |select * from test_table where id=1                   | success       | mytest |
    Then execute sql in "dble-1" use "admin"
        | user | passwd | conn   | toClose  | sql                         | expect                             | db     |
        | root | 111111 | conn_0 | True     | show @@cache               | length{(2)}| |