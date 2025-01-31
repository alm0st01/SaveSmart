const { connectToDatabase } = require('./mongodb');

async function loginUser(email, password) {
  const client = await connectToDatabase();
  try {
    const database = client.db('info');
    const users = database.collection('accountcreds');

    const result = await users.find({ email: email });
    console.log(`User found with the id: ${result[0]._id}`);
  } catch (error) {
    console.error("Error signing up user", error);
  } finally {
    await client.close();
  }
}

module.exports = { loginUser };