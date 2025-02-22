import React from "react";

const BACKGROUND_URL =
  "https://static.vecteezy.com/system/resources/previews/012/996/585/non_2x/cars-on-road-tropical-palms-cartoon-illustration-free-vector.jpg";

function Login() {
  return (
    <div style={styles.pageWrapper}>
      <div style={styles.loginBox}>
        <h1 style={styles.title}>Welcome to ShareRides!</h1>

        {/* Google Sign-In Button/Placeholder */}
        <button style={styles.googleButton}>
          <img
            src="https://wpdiscuz.com/wp-content/uploads/wpforo/attachments/125817/3813-NewLogo.png"
            alt="Google G Logo"
            style={styles.googleIcon}
          />
          Sign in with Google
        </button>

        {/* Guest Sign-In Link/Placeholder */}
        <p style={styles.guestLink}>Sign in as Guest</p>
      </div>
    </div>
  );
}

const styles = {
  pageWrapper: {
    /* Full viewport coverage */
    width: "100vw",
    height: "100vh",
    margin: 0,
    padding: 0,

    /* Background image styling */
    backgroundImage: `url(${BACKGROUND_URL})`,
    backgroundSize: "cover",
    backgroundPosition: "center",

    /* Center the login box */
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  loginBox: {
    backgroundColor: "rgba(255, 255, 255, 0.9)",
    border: "2px solid #ccc",
    borderRadius: "8px",
    padding: "2rem 3rem",
    textAlign: "center",
    maxWidth: "600px",
    width: "90%",
  },
  title: {
    marginBottom: "2rem",
    fontSize: "2rem",
    color: "#333",
  },
  googleButton: {
    display: "inline-flex",
    alignItems: "center",
    backgroundColor: "#fff",
    color: "#000",
    border: "1px solid #ccc",
    borderRadius: "4px",
    padding: "0.75rem 1.5rem",
    cursor: "pointer",
    fontSize: "1rem",
  },
  googleIcon: {
    width: "20px",
    marginRight: "8px",
  },
  guestLink: {
    marginTop: "1rem",
    textDecoration: "underline",
    color: "#007bff",
    cursor: "pointer",
  },
};

export default Login;
