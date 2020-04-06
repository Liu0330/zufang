drop database if exists hrs;
create database hrs default charset utf8;

use hrs;

drop table if exists tb_emp;
drop table if exists tb_dept;

create table tb_dept
(
dno int not null comment '���',
dname varchar(10) not null comment '����',
dloc varchar(20) not null comment '���ڵ�',
primary key (dno)
);

insert into tb_dept values
	(10, '��Ʋ�', '����'),
	(20, '�з���', '�ɶ�'),
	(30, '���۲�', '����'),
	(40, '��ά��', '����');

create table tb_emp
(
eno int not null comment 'Ա�����',
ename varchar(20) not null comment 'Ա������',
job varchar(20) not null comment 'Ա��ְλ',
mgr int comment '���ܱ��',
sal int not null comment 'Ա����н',
comm int comment 'ÿ�²���',
dno int comment '���ڲ��ű��',
primary key (eno)
);

alter table tb_emp add constraint fk_emp_mgr foreign key (mgr) references tb_emp (eno);
alter table tb_emp add constraint fk_emp_dno foreign key (dno) references tb_dept (dno);

insert into tb_emp values
	(7800, '������', '�ܲ�', null, 9000, 1200, 20),
	(2056, '�Ƿ�', '����ʦ', 7800, 5000, 1500, 20),
	(3088, '��Ī��', '���ʦ', 2056, 3500, 800, 20),
	(3211, '���޼�', '����Ա', 2056, 3200, null, 20),
	(3233, '�𴦻�', '����Ա', 2056, 3400, null, 20),
	(3251, '�Ŵ�ɽ', '����Ա', 2056, 4000, null, 20),
	(5566, '��Զ��', '���ʦ', 7800, 4000, 1000, 10),
	(5234, '����', '����', 5566, 2000, null, 10),
	(3344, '����', '��������', 7800, 3000, 800, 30),
	(1359, '��һ��', '����Ա', 3344, 1800, 200, 30),
	(4466, '���˷�', '����Ա', 3344, 2500, null, 30),
	(3244, 'ŷ����', '����Ա', 3088, 3200, null, 20),
	(3577, '���', '���', 5566, 2200, null, 10),
	(3588, '�����', '���', 5566, 2500, null, 10);