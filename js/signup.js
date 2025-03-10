const { connectToDatabase } = require('./mongodb');

async function signupUser(username, password, firstName, lastName, email) {
  const client = await connectToDatabase();
  try {
    const database = client.db('info');
    const users = database.collection('accountcreds');

    const result = await users.insertOne({ username, password, firstName, lastName, email });
    console.log(`New user created with the following id: ${result.insertedId}`);
  } catch (error) {
    console.error("Error signing up user", error);
  } finally {
    await client.close();
  }
}

module.exports = { signupUser };