import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';

const PostReview = () => {
  const [dealer, setDealer] = useState(null);
  const [review, setReview] = useState("");
  const [model, setModel] = useState("");
  const [year, setYear] = useState("");
  const [date, setDate] = useState("");
  const [carmodels, setCarmodels] = useState([]);
  
  const params = useParams();
  const navigate = useNavigate();
  const id = params.id;

  // Construcción de URLs usando window.location.origin para mayor estabilidad
  const root_url = window.location.origin;
  const dealer_url = `${root_url}/djangoapp/dealer/${id}/`;
  const review_url = `${root_url}/djangoapp/add_review/`;
  const carmodels_url = `${root_url}/djangoapp/get_cars/`;

  const get_dealer = async () => {
    try {
      const res = await fetch(dealer_url);
      const retobj = await res.json();
      if (retobj.status === 200 && retobj.dealer) {
        // Normalizamos el objeto dealer
        const data = Array.isArray(retobj.dealer) ? retobj.dealer[0] : retobj.dealer;
        setDealer(data);
      }
    } catch (err) {
      console.error("Error cargando dealer:", err);
    }
  };

  const get_cars = async () => {
    try {
      const res = await fetch(carmodels_url);
      const retobj = await res.json();
      
      // Verificamos la estructura: algunos backends devuelven CarModels o la lista directa
      if (retobj.CarModels) {
        setCarmodels(retobj.CarModels);
      } else if (Array.isArray(retobj)) {
        setCarmodels(retobj);
      }
    } catch (err) {
      console.error("Error cargando coches:", err);
    }
  };

  useEffect(() => {
    get_dealer();
    get_cars();
  }, [id]);

  const postreview = async () => {
    let name = sessionStorage.getItem("firstname") + " " + sessionStorage.getItem("lastname");
    if (name.includes("null") || name.trim() === "") {
      name = sessionStorage.getItem("username");
    }

    if (!model || review === "" || date === "" || year === "") {
      alert("All details are mandatory");
      return;
    }

    const [make_chosen, ...model_parts] = model.split(" ");
    const model_chosen = model_parts.join(" ");

    const jsoninput = JSON.stringify({
      "name": name,
      "dealership": id,
      "review": review,
      "purchase": true,
      "purchase_date": date,
      "car_make": make_chosen,
      "car_model": model_chosen,
      "car_year": year,
    });

    try {
      const res = await fetch(review_url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: jsoninput,
      });

      const json = await res.json();
      if (json.status === 200) {
        // Redirección segura usando el origen de la ventana
        window.location.href = `${window.location.origin}/dealer/${id}`;
      }
    } catch (err) {
      console.error("Error al publicar review:", err);
    }
  };

  // Cláusula de guarda para evitar errores de 'undefined'
  if (!dealer) {
    return (
      <div>
        <Header />
        <div style={{ margin: "5%" }}>
          <h1 style={{ color: "grey" }}>Cargando formulario de reseña...</h1>
        </div>
      </div>
    );
  }

 return (
    <div>
      <Header/>
      <div style={{margin:"5%", textAlign: "left"}}>
        <h1 style={{color:"darkblue"}}>{dealer.full_name}</h1>
        
        {/* Contenedor de la Reseña */}
        <div style={{marginBottom: "20px"}}>
          <label style={{display: "block", fontWeight: "bold"}}>Review Content</label>
          <textarea 
            id='review' 
            cols='50' 
            rows='7' 
            onChange={(e) => setReview(e.target.value)}
            style={{width: "100%", maxWidth: "600px"}}
          ></textarea>
        </div>

        {/* Campos de Entrada Alineados */}
        <div className='input_field'>
          <label>Purchase Date:</label>
          <input type="date" onChange={(e) => setDate(e.target.value)}/>
        </div>

        <div className='input_field'>
          <label>Car Model:</label>
          <select name="cars" id="cars" onChange={(e) => setModel(e.target.value)}>
            <option value="" selected disabled hidden>Choose Car Make and Model</option>
            {carmodels.map((carmodel, index) => (
                <option key={index} value={carmodel.car_make + " " + carmodel.car_model}>
                  {carmodel.car_make} {carmodel.car_model}
                </option>
            ))}
          </select>
        </div>

        <div className='input_field'>
          <label>Car Year:</label>
          <input 
            type="number" 
            onChange={(e) => setYear(e.target.value)} 
            max={2026} 
            min={2015}
            style={{width: "100px"}}
          />
        </div>

        <div style={{marginTop: "30px"}}>
          <button className='postreview' onClick={postreview}>Post Review</button>
        </div>
      </div>
    </div>
);
};

export default PostReview;