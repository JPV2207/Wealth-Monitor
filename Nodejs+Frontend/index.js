import express from "express";
import bodyParser from "body-parser";
import mysql from "mysql";
import bcrypt from "bcrypt";
import passport from "passport";
import { Strategy } from "passport-local";
import GoogleStrategy from "passport-google-oauth2";
import session from "express-session";
import flash from "connect-flash";
import multer from "multer";
import env from "dotenv";
import path from "path";
import fs from "fs";
import nodemailer from "nodemailer";
import jwt from "jsonwebtoken";
import fetch from "node-fetch";
import crypto from "crypto";
import Swal from 'sweetalert2';


// Create an Express application
const app = express();

// Set the port number
const port = 3000;

// Number of salt rounds for bcrypt
const saltRounds = 10;

// Load environment variables from .env file
env.config();

// Create a MySQL connection pool
const pool = mysql.createPool({
  connectionLimit: 10,
  host: process.env.MYSQL_HOST,
  user: process.env.MYSQL_USER,
  password: process.env.MYSQL_PASSWORD,
  database: process.env.MYSQL_DATABASE
});


// Configure Nodemailer for sending emails
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// Function to generate a random token
const generateToken = () => {
  return crypto.randomBytes(20).toString('hex');
};


// Configure Multer for handling file uploads
const storage = multer.diskStorage({
  destination: function(req, file, cb) {
    cb(null, 'uploads/'); // Specify the destination directory for uploaded files
  },
  filename: function(req, file, cb) {
    cb(null, file.fieldname + '-' + Date.now() + path.extname(file.originalname)) // Rename the uploaded file
  }
});
const upload = multer({
  storage: storage
});


// Serve static files from the 'public' directory
const __dirname = path.resolve();
app.use(express.static("public"));

// Serve static files from the 'views' directory
app.use(express.static(path.join(__dirname, 'views')));



// Serve files from the 'uploads' directory
app.use("/uploads", express.static(path.join(__dirname, "uploads")));


// Configure sessions
app.use(
  session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: true,
    cookie: {
     maxAge: 2 * 60 * 60 * 1000 // 2 hours in milliseconds
   }
  })
);


// Parse incoming request bodies
app.use(bodyParser.urlencoded({
  extended: true
}));


// Initialize Passport
app.use(passport.initialize());
app.use(passport.session());


// Flash messages middleware
app.use(flash());


// Route to render the home page
app.get("/", (req, res) => {
  res.render("wealthmonitor.ejs");
});


// Route to handle the analyze button click
app.get("/analyze", (req, res) => {
  // Redirect the user to 127.0.0.1:5000
  res.redirect("http://127.0.0.1:5000");
});


// Route to handle the analyze button click
app.post("/analyze", async (req, res) => {
  try {
    console.log("Analyze route triggered");
    const defaultEmail = "default@example.com"; // Hardcoded default email
    console.log("Attempting to send email to Flask server for analysis...");
    await sendEmailToFlask(defaultEmail);
    console.log("Email sent to Flask server for analysis successfully");
    res.json({ success: true });
  } catch (error) {
    console.error("Error sending email to Flask server for analysis:", error);
    res.status(500).json({ success: false });
  }
});



// Route to render the register page
app.get("/register", (req, res) => {
  res.render("register.ejs");
});


// Route to handle the click on Login/Register button and redirect to the register page
app.get("/login-register", (req, res) => {
  res.redirect("/register");
});


// Route to handle user registration
app.post("/register", async (req, res) => {
  const email = req.body.username;
  const password = req.body.password;
  const fName = req.body.firstname;
  const lName = req.body.lastname;
  try {
    const query = "SELECT * FROM users WHERE email = ?";
    pool.query(query, [email], async (error, results) => {
      if (error) {
        console.error("Error checking if user exists:", error);
        res.status(500).send("Internal Server Error");
      } else {
        if (results.length > 0) {
          res.redirect("/login");
        } else {
          bcrypt.hash(password, saltRounds, async (err, hash) => {
            if (err) {
              console.error("Error hashing password:", err);
              res.status(500).send("Internal Server Error");
            } else {
              const query = "INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)";
              pool.query(query, [fName, lName, email, hash], (error, results) => {
                if (error) {
                  console.error("Error registering user:", error);
                  res.status(500).send("Internal Server Error");
                } else {
                  const user = {
                    id: results.insertId,
                    email,
                    password: hash
                  }; // Assuming insertId as the new user's id
                  req.login(user, (err) => {
                    if (err) {
                      console.error("Error logging in user:", err);
                      res.status(500).send("Internal Server Error");
                    } else {
                      console.log("User registered successfully");
                      // Send email to Flask server
                      sendEmailToFlask(email);
                      res.redirect("/secrets");
                    }
                  });
                }
              });
            }
          });
        }
      }
    });
  } catch (err) {
    console.error("Error registering user:", err);
    res.status(500).send("Internal Server Error");
  }
});

// Route to render the login page
app.get("/login", (req, res) => {
  res.render("login.ejs");
});




//const token = jwt.sign({ username: email }, "1234");
// Configure passport
import { Strategy as LocalStrategy } from 'passport-local';
 // Import LocalStrategy from passport-local
passport.use(new LocalStrategy(
    {
        usernameField: 'email', // Assuming the login form has an input field with name 'email'
        passwordField: 'password' // Assuming the login form has an input field with name 'password'
    },
    function(email, password, done) {
        // Validate the email and password here
        // Example: Assume the user is authenticated if email and password match
        if (email === usernameField && password === passwordField) {
            return done(null, { email: email });
        } else {
            return done(null, false, { message: 'Invalid credentials' });
        }
    }
));

// Middleware to initialize passport
app.use(passport.initialize());


// Route to handle user login
app.post("/login", (req, res) => {
    console.log("Login request received:", req.body);
    passport.authenticate("local", (err, user, info) => {
        if (err) {
            console.error("Error authenticating user:", err);
            return res.status(500).json({ message: "Internal Server Error" });
        }
        if (!user) {
            //console.log("Authentication failed:", info.message);
            return res.status(401).json({ message: "Invalid credentials" });
        }
        req.login(user, { session: false }, (err) => {
            if (err) {
                console.error("Error logging in user:", err);
                return res.status(500).json({ message: "Internal Server Error" });
            }
            console.log("User logged in successfully:", user.email);
            // Send email to Flask server
            sendEmailToFlask(user.email)
                .then(() => {
                    res.redirect("/secrets");
                })
                .catch(error => {
                    console.error("Error sending email to Flask server:", error);
                    res.status(500).json({ message: "Internal Server Error" });
                });
        });
    })(req, res);
});



// Function to send email to Flask server
function sendEmailToFlask(email) {
  return fetch('http://127.0.0.1:5000/receive_email', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email: email }) // Sending email data as JSON
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to send email to Flask: ' + response.statusText);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    throw error;
  });
}


// Route to log out the user
app.get("/logout", (req, res) => {
  console.log("Logging out user:", req.user);
  console.log("Session data before logout:", req.session); // Log session data before logout
  req.logout(function(err) {
    if (err) {
      console.error("Error logging out user:", err);
      return next(err);
    }
    console.log("User logged out successfully");
    console.log("Session data after logout:", req.session); // Log session data after logout
    res.redirect("/");
  });
});


// Route to render the secrets page if the user is authenticated, otherwise redirect to the login page
app.get("/secrets", (req, res) => {
  console.log("User Authenticated:", req.isAuthenticated());
  if (req.isAuthenticated()) {
    console.log("Authenticated User:", req.user);
    const uploadsDir = path.join(__dirname, "uploads");
    res.render("secrets.ejs", {
      user: req.user,
      uploadsDir: uploadsDir
    });
  } else {
    console.log("User not authenticated. Redirecting to login page.");
    res.redirect("/login");
  }
});


// Route to render the update profile page if the user is authenticated, otherwise redirect to the login page
app.get("/update-profile", (req, res) => {
  if (req.isAuthenticated()) {
    try {
      const query = "SELECT * FROM users WHERE id = ?";
      pool.query(query, [req.user.id], (error, results) => {
        if (error) {
          console.error("Error fetching updated user profile:", error);
          res.redirect("/update-profile");
        } else {
          const updatedUser = results[0];
          req.user = updatedUser;
          res.render("update-profile.ejs", {
            user: req.user,
            message: req.flash('updateMessage')
          });
        }
      });
    } catch (err) {
      console.error("Error fetching updated user profile:", err);
      res.redirect("/update-profile");
    }
  } else {
    res.redirect("/login");
  }
});


// Route to handle updating user profile
app.post("/update-profile", upload.single('profileImage'), async (req, res) => {
  if (req.isAuthenticated()) {
    const { first_name, last_name } = req.body;
    let profileImage = req.user.profile_image; // Get the current profile image filename
    if (req.file) {
      profileImage = req.file.filename; // Update profile image if a new image is uploaded
    }
    try {
      const query = "UPDATE users SET first_name = ?, last_name = ?, profile_image = ? WHERE id = ?";
      pool.query(query, [first_name, last_name, profileImage, req.user.id], (error) => {
        if (error) {
          console.error("Error updating user profile:", error);
          req.flash('updateMessage', 'An error occurred while updating your profile.');
          res.redirect("/update-profile");
        } else {
          console.log("User profile updated successfully");
          req.user.profile_image = profileImage; // Update profile image in user object
          req.session.passport.user = req.user; // Update user session with updated user object
          res.redirect("/secrets");
        }
      });
    } catch (err) {
      console.error("Error updating user profile:", err);
      req.flash('updateMessage', 'An error occurred while updating your profile.');
      res.redirect("/update-profile");
    }
  } else {
    res.redirect("/login");
  }
});



// Route to render the password reset form
app.get('/reset-password', (req, res) => {
  res.render('send-email.ejs');
});


// Route to handle the password reset request
app.post('/reset-password', async (req, res) => {
  const { email } = req.body;

  // Retrieve the email address associated with the provided username from the database
  const query = "SELECT email FROM users WHERE email = ?";
  pool.query(query, [email], (error, results) => {
    if (error) {
      console.error("Error fetching user email:", error);
      res.status(500).send('Internal Server Error');
    } else {
      if (results.length === 0) {
        // User with the provided email does not exist
        res.status(404).send('User not found');
      } else {
        const userEmailAddress = results[0].email;
        const token = generateToken(); // Generate a reset token
        const expirationTime = new Date(Date.now() + 3600000); // Token expiration time (1 hour from now)

        // Store the token and its expiration time in the database
        const updateQuery = "UPDATE users SET reset_token = ?, reset_token_expiration = ? WHERE email = ?";
        pool.query(updateQuery, [token, expirationTime, email], (updateError, updateResults) => {
          if (updateError) {
            console.error("Error updating reset token:", updateError);
            res.status(500).send('Internal Server Error');
          } else {
            // Compose the email
            const mailOptions = {
              from: '"Wealth Monitor"<jaiprkashvalecha73@gmail.com>', // Set a default sender name and email address
              to: userEmailAddress,
              subject: 'Password Reset Request',
              html: `<p>You are receiving this email because you (or someone else) has requested a password reset for your account.</p>
                     <p>Please click on the following link to reset your password:</p>
                     <p><a href="http://localhost:3000/reset-password/${token}">Reset Password</a></p>
                     <p>If you did not request this, please ignore this email and your password will remain unchanged.</p>`
            };

            // Send the email
            transporter.sendMail(mailOptions, (mailError, info) => {
              if (mailError) {
                console.error('Error sending email:', mailError);
                res.status(500).send('Internal Server Error');
              } else {
                console.log('Email sent:', info.response);
                res.render('send-email.ejs', { successMessage: 'Email sent successfully.' });
              }
            });
          }
        });
      }
    }
  });
});


// Route to initiate Google authentication
app.get(
  "/auth/google",
  passport.authenticate("google", {
    scope: ["profile", "email"],
  })
);


// Route to handle Google authentication callback
app.get(
  "/auth/google/secrets",
  passport.authenticate("google", {
    successRedirect: "/secrets",
    failureRedirect: "/login?error=wrongPassword", // Add query parameter for wrong password
  })
);


// Route to render the password reset form with token verification
app.get('/reset-password/:token', (req, res) => {
  const token = req.params.token;
  // Verify the token from the database (optional)
  // If token is valid, render the reset password form
  res.render('reset-password-form.ejs', {
    token
  });
});


// Route to handle the password reset form submission
app.post('/reset-password/:token', (req, res) => {
  const token = req.params.token;
  const newPassword = req.body.newPassword;

  // Update the password in the database
  const query = "UPDATE users SET password = ?, reset_token = NULL, reset_token_expiration = NULL WHERE reset_token = ?";
  bcrypt.hash(newPassword, saltRounds, (err, hash) => {
    if (err) {
      console.error("Error hashing password:", err);
      res.status(500).send('Internal Server Error');
    } else {
      pool.query(query, [hash, token], (error, results) => {
        if (error) {
          console.error("Error updating password:", error);
          res.status(500).send('Internal Server Error');
        } else {
          console.log("Password updated successfully");
          res.redirect('/login');
        }
      });
    }
  });
});


// Local strategy for Passport authentication
passport.use(
  "local",
  new Strategy(async function verify(username, password, cb) {
    try {
      const query = "SELECT * FROM users WHERE email = ?";
      pool.query(query, [username], async (error, results) => {
        if (error) {
          console.error("Error finding user:", error);
          return cb(error);
        } else {
          if (results.length > 0) {
            const user = results[0];
            const storedHashedPassword = user.password;
            bcrypt.compare(password, storedHashedPassword, (err, valid) => {
              if (err) {
                console.error("Error comparing passwords:", err);
                return cb(err);
              } else {
                if (valid) {
                  return cb(null, user);
                } else {
                  return cb(null, false);
                }
              }
            });
          } else {
            return cb(null, false);
          }
        }
      });
    } catch (err) {
      console.error("Error finding user:", err);
      return cb(err);
    }
  })
);


// Google OAuth2 strategy for Passport authentication
passport.use(
  "google",
  new GoogleStrategy({
      clientID: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
      callbackURL: "http://localhost:3000/auth/google/secrets",
      userProfileURL: "https://www.googleapis.com/oauth2/v3/userinfo",
    },
    async (accessToken, refreshToken, profile, cb) => {
      try {
        const query = "SELECT * FROM users WHERE email = ?";
        pool.query(query, [profile.email], async (error, results) => {
          if (error) {
            console.error("Error finding user:", error);
            return cb(error);
          } else {
            if (results.length === 0) {
              // If the user doesn't exist, create a new user with Google information
              const newUser = {
                email: profile.email,
                first_name: profile.given_name,
                last_name: profile.family_name,
                profile_image: profile.picture,
              };
              const insertQuery = "INSERT INTO users SET ?";
              pool.query(insertQuery, newUser, (error, results) => {
                if (error) {
                  console.error("Error registering user:", error);
                  return cb(error);
                } else {
                  newUser.id = results.insertId;
                  return cb(null, newUser);
                }
              });
            } else {
              // If the user already exists, return the user
              return cb(null, results[0]);
            }
          }
        });
      } catch (err) {
        console.error("Error finding user:", err);
        return cb(err);
      }
    }
  )
);


// Serialize and deserialize user for session management
passport.serializeUser((user, cb) => {
  console.log("Serializing user:", user);
  cb(null, user);
});

passport.deserializeUser((user, cb) => {
  console.log("Deserializing user:", user);
  cb(null, user);
});


// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
