const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const { MongoClient, ServerApiVersion } = require('mongodb');
require('dotenv').config()


const app = express();
const port = 3000;


const uri = process.env.MONGO_URI;

const client = new MongoClient(uri, { serverApi: ServerApiVersion.v1 });

async function connectToDatabase() {
  try {

    await client.connect();
    console.log("Connected to MongoDB!");
    return client;
  } catch (err) {
    console.error("Failed to connect to MongoDB", err);
    throw err;
  }
}


app.use(express.static(path.join(__dirname, '../')));

app.use(bodyParser.urlencoded({ extended: true }));

app.post('/signup', async (req, res) => {
  const { username, password, firstName, lastName, email } = req.body;
  try {
    const client = await connectToDatabase();
    const db = client.db('info');
    const collection = db.collection('accountcreds');

    console.log("hi");
    const existingUsername = await collection.findOne({'username': username});
    const existingEmail = await collection.findOne({'email': email});
    console.log("hey");
    console.log("hello");
    if (existingUsername != null){
        res.send(`<script>alert("Your username needs to be original."); window.location.href = "/account/auth/signup/index.html";</script>`);    
    }
    else if (existingEmail != null){
        res.send(`<script>alert("Your email needs to be original."); window.location.href = "/account/auth/signup/index.html";</script>`);    
    }
    else {
        const result = await collection.insertOne({ username, password, firstName, lastName, email });
        console.log(`New user created with the following id: ${result.insertedId}`);
        res.send(`<script>alert("Signup successful!"); window.location.href = "/";</script>`);
    }
  } catch (error) {
    console.error("Error signing up user", error);
    res.send(`<script>alert("Error signing up user"); window.location.href = "/account/auth/signup/index.html";</script>`);
  } finally {
    await client.close();
  }
});

app.post('/login', async (req, res) => {
    const { email, password} = req.body;

  try {
    const client = await connectToDatabase();
    const database = client.db('info');
    const collection = database.collection('accountcreds');

    const user = await collection.findOne({ "email": email }); // Checking email
    console.log(user);
    console.log(`User found with the id: ${user._id}`);

    if (password === user.password){ // Checking if the User ID matches up with the password
        res.send(`<script>alert("Login successful!"); window.location.href = "/";</script>`);
    }
    else {
        throw "User login information is incorrect."
    }
  } catch (error) {
    console.error("Error signing up user:", error);
    res.send(`<script>alert("Email or password is incorrect"); window.location.href = "/account/auth/login/index.html";</script>`);
  } finally {
    await client.close();
  }
  });

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../signup/index.html'));
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});