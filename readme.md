# Snake BnB
參考教學影片
[MongoDB with Python Crash Course](https://www.youtube.com/watch?v=E-1xI85Zog8&list=PLYHrAQFR-2VONBMZsOPbDQy_MYlC3rxe4&index=2&ab_channel=freeCodeCamp.org)
> 終端機形式的Snake BnB，以顧客或籠主身分登入，操作籠子可入住時段、預約籠子、註冊寵物蛇等
> 
> > master 分支為教學影片主軸
> > trySome 分支則是自己嘗試各種東西用的

![image](/static/gif/host_action.gif)
![image](/static/gif/guest_action.gif)

---
使用工具:
* [MongoDB](https://www.mongodb.com/)
    * 一種文件導向的資料庫管理系統。可先想像成一種很彈性的資料庫，例如儲存鍵盤資料，一筆可以只存3項資料，而另一筆可依需求調整
    ```json
      {
        "name":"keyboard1",
        "color":"blue",
        "size":"big",
      }
      {
        "name":"keyboard2",
        "color":"orange",
        "size":"small",
        "light":"rgb",
      }
    ```
* [venv](https://docs.python.org/3/library/venv.html)
  * python 虛擬環境
* [mongoengine](https://docs.mongoengine.org/tutorial.html#)
  * Python透過它操作MongoDB，如同[ORM](https://ithelp.ithome.com.tw/articles/10207752)的角色
* [Robo 3T](https://robomongo.org/)
  * MongoDB GUI (Graphical User Interface)，方便的使用者介面，用來直接操作MongoDB，資料呈現更易讀，也可撰寫原生語法嘗試執行結果等，因此還是要懂[MongoDB原生語法](https://docs.mongodb.com/manual/crud/#mongodb-crud-operations)

---

#### 執行專案步驟 (Windows環境)
1. clone 專案
2. 使用cmd終端機，進入專案
3. 輸入`python -m venv .env`，產生虛擬環境設定資料夾
4. 輸入`.env\Scripts\activate.bat`，啟動並進入虛擬環境，留意你的終端機目前位置最前面會有`(.env)`
   * ，若要離開虛擬環境，輸入`deactivate`
5. 輸入`pip install -r requirements.txt`，安裝requirements.txt中指定的套件
6. 輸入`python ./src/program.py`，進入主程式

---

#### 簡略紀錄
>更完整的用法請查詢[mongoengine官方文件](https://docs.mongoengine.org/guide/querying.html#querying-the-database)

Inserting
```python
snakes = []
snakes.append(snake1)
snakes.append(snake2)

Snake.objects().insert(snakes)
```
Direct match
```python
# 取一筆符合的資料，沒有符合的資料則會得到 None
Owner.objects().filter(email=email).first()
```
subdocuments
```python
# 用更下一層的資料比對
def get_bookings_for_user(user_id: ObjectID) -> List[Booking]:
  owner = Owner.objects(id=user_id).first()
  # \ 符號可幫助讓程式碼更易讀
  # bookings__guest_snake_id__in
  # 第一層欄位 __ 第二層欄位 __ operators
  # 不同意義的參數用 雙底線區隔
  booked_cages = Cage \
        .objects(bookings__guest_snake_id__in=owner.snake_ids) \
        .all()

  return list(booked_cages)
```
[operators](https://docs.mongoengine.org/guide/querying.html#query-operators)
```python
cages = Cage.objects().filter(square_meters__gte=min_size)

cage_count = Cage.objects(square_meters__gte=min_size).count()
```
[Atomic updates](https://docs.mongoengine.org/guide/querying.html#atomic-updates)
```python
BlogPost.objects(id=post.id).update_one(set__title='Example Post')

BlogPost.objects(id=post.id).update_one(push__tags='nosql')
```
設計概念：Collections是否要嵌入另一Collections中?
1. Is the embedded data wanted 80% of the time?
2. How often do you want the embedded data without the containing document?
3. Is the embedded data a bounded set?
4. Is that bound small?
5. How varied are your queries?
6. Is this an integration DB or an application DB(good for MongoDB)?

---
參考資料:
* [教學者的範例Github](https://github.com/mikeckennedy/mongodb-quickstart-course)
* [[Day20] 資料庫設計概念 - ORM - iT 邦幫忙](https://ithelp.ithome.com.tw/articles/10207752)
* [MongoDB Document](https://docs.mongodb.com/manual/crud/)
* [MongoEngine User Documentation](https://docs.mongoengine.org/index.html)
