"""Description для API документации роутера devices."""

LIST_DEVICES = """
Возвращает список устройств с поддержкой фильтрации и сортировки.

Query-параметры:
- search — поиск по inventoryNumber, name, serialNumber
- status — фильтр по статусу (или all)
- type — фильтр по deviceTypeId (или all)
- location — фильтр по locationId (или all)
- person — фильтр по personId (или all)
- sort — поле сортировки: inventoryNumber, name, status, commissionDate
- order — asc или desc
"""
GET_DEVICE = "Возвращает устройство по ID. 404 если не найдено."
CREATE_DEVICE = "Создаёт новое устройство. ID генерируется на сервере."
UPDATE_DEVICE = "Обновляет устройство. Можно передать только изменённые поля."
DELETE_DEVICE = "Удаляет (списывает) устройство."
GET_DEVICE_AUDIT = "Возвращает историю изменений устройства."
