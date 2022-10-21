DROP TABLE IF EXISTS tickets;
CREATE TABLE tickets (
	number INTEGER PRIMARY KEY AUTOINCREMENT,
	cost INTEGER DEFAULT NULL,
	day_of_purchase TEXT DEFAULT NULL,
	time_of_purchase TEXT DEFAULT NULL,
	type TEXT NOT NULL,
     
	CHECK(cost != '' AND type != '')

	CONSTRAINT buyers_tickets_fk
		FOREIGN KEY (number) REFERENCES buyers(ticket_numbers) ON DELETE RESTRICT
);

DROP TABLE IF EXISTS buyers;
CREATE TABLE buyers (
    ticket_number INTEGER PRIMARY KEY,
	second_name TEXT NOT NULL,
	name TEXT NOT NULL,
	phone_number TEXT UNIQUE NOT NULL,
	vk_link TEXT DEFAULT NULL,
	is_inside INTEGER DEFAULT 0,

	CHECK(second_name != '' AND name != '' AND phone_number != '' AND vk_link != '' AND ticket_number != ''),

	CONSTRAINT buyers_tickets_fk
		FOREIGN KEY (ticket_number) REFERENCES tickets(number) ON DELETE RESTRICT

);